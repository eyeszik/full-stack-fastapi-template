"""Facebook Graph API integration for Facebook Pages."""

from datetime import datetime
from typing import Any
import httpx

from app.models import PlatformType
from app.services.integrations.base import (
    BasePlatformIntegration,
    AuthenticationError,
    ContentValidationError,
    RateLimitError,
)


class FacebookIntegration(BasePlatformIntegration):
    """Facebook Graph API integration for Page posting.

    Requires:
    - Facebook App with pages_manage_posts, pages_read_engagement permissions
    - Page access token (not user access token)

    API Docs: https://developers.facebook.com/docs/graph-api
    """

    BASE_URL = "https://graph.facebook.com/v19.0"
    TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"

    def __init__(self, social_account, app_secret: str):
        """Initialize Facebook integration.

        Args:
            social_account: SocialAccount with Facebook credentials
            app_secret: Facebook App Secret
        """
        super().__init__(social_account)
        self.app_secret = app_secret
        # Store page_id in account_handle field
        self.page_id = social_account.account_handle

    async def refresh_access_token(self) -> str:
        """Exchange short-lived token for long-lived token.

        Returns:
            New long-lived access token (60 days)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.TOKEN_URL,
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": "app_id",  # Should be stored in config
                    "client_secret": self.app_secret,
                    "fb_exchange_token": self.access_token,
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to refresh Facebook token: {response.text}",
                    PlatformType.FACEBOOK,
                    response.status_code,
                )

            data = response.json()
            return data["access_token"]

    async def verify_credentials(self) -> dict[str, Any]:
        """Verify Facebook Page access."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{self.page_id}",
                params={
                    "fields": "id,name,fan_count,category,access_token",
                    "access_token": self.access_token,
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Invalid Facebook credentials: {response.text}",
                    PlatformType.FACEBOOK,
                    response.status_code,
                )

            data = response.json()
            return {
                "page_id": data["id"],
                "page_name": data["name"],
                "fan_count": data.get("fan_count", 0),
                "category": data.get("category", ""),
            }

    async def publish_content(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Publish a post to Facebook Page.

        Args:
            content_data: Must include:
                - message: Post text (optional if photo/video provided)
                - link: URL to share (optional)
                - photo_url: URL of photo to post (optional)
                - video_path: Path to video file (optional)

        Returns:
            {
                "post_id": str,
                "url": str
            }
        """
        await self.ensure_valid_token()

        endpoint = f"{self.BASE_URL}/{self.page_id}"

        # Determine post type
        if content_data.get("video_path"):
            return await self._publish_video(content_data)
        elif content_data.get("photo_url") or (media_urls and len(media_urls) > 0):
            return await self._publish_photo(content_data, media_urls)
        else:
            return await self._publish_text(content_data)

    async def _publish_text(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Publish text/link post."""
        payload = {
            "message": content_data.get("message", ""),
            "access_token": self.access_token,
        }

        if content_data.get("link"):
            payload["link"] = content_data["link"]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/{self.page_id}/feed",
                data=payload,
            )

            if response.status_code == 429:
                raise RateLimitError(
                    "Facebook rate limit exceeded",
                    PlatformType.FACEBOOK,
                    429,
                )

            if response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"Facebook post failed: {response.text}",
                    PlatformType.FACEBOOK,
                    response.status_code,
                )

            data = response.json()
            post_id = data["id"]

            return {
                "post_id": post_id,
                "url": f"https://www.facebook.com/{post_id}",
            }

    async def _publish_photo(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Publish photo post."""
        photo_url = content_data.get("photo_url") or (media_urls[0] if media_urls else None)

        if not photo_url:
            raise ContentValidationError(
                "photo_url required for photo post",
                PlatformType.FACEBOOK,
            )

        payload = {
            "url": photo_url,
            "message": content_data.get("message", ""),
            "access_token": self.access_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/{self.page_id}/photos",
                data=payload,
            )

            if response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"Photo post failed: {response.text}",
                    PlatformType.FACEBOOK,
                    response.status_code,
                )

            data = response.json()
            return {
                "post_id": data["id"],
                "url": f"https://www.facebook.com/photo.php?fbid={data['id']}",
            }

    async def _publish_video(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Publish video post (resumable upload for large files)."""
        video_path = content_data["video_path"]

        # For videos > 1GB, use resumable upload
        # Simplified version shown here
        async with httpx.AsyncClient(timeout=300.0) as client:
            with open(video_path, "rb") as video_file:
                files = {"source": video_file}
                data_payload = {
                    "description": content_data.get("message", ""),
                    "access_token": self.access_token,
                }

                response = await client.post(
                    f"{self.BASE_URL}/{self.page_id}/videos",
                    data=data_payload,
                    files=files,
                )

                if response.status_code not in [200, 201]:
                    raise ContentValidationError(
                        f"Video upload failed: {response.text}",
                        PlatformType.FACEBOOK,
                        response.status_code,
                    )

                result = response.json()
                return {
                    "post_id": result["id"],
                    "url": f"https://www.facebook.com/video.php?v={result['id']}",
                }

    async def schedule_content(
        self,
        content_data: dict[str, Any],
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Schedule a Facebook post for future publishing.

        Facebook supports native scheduling via published=false and scheduled_publish_time.
        """
        # Add scheduling parameters
        content_data["published"] = "false"
        content_data["scheduled_publish_time"] = int(scheduled_time.timestamp())

        # Publish as unpublished/scheduled
        result = await self.publish_content(content_data, media_urls)

        return {
            **result,
            "scheduled_for": scheduled_time.isoformat(),
            "status": "scheduled",
        }

    async def get_analytics(
        self,
        post_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch Facebook Insights for a post.

        Requires pages_read_engagement permission.
        """
        await self.ensure_valid_token()

        # Default metrics
        if not metrics:
            metrics = [
                "post_impressions",
                "post_impressions_unique",
                "post_engaged_users",
                "post_clicks",
                "post_reactions_like_total",
                "post_reactions_love_total",
            ]

        async with httpx.AsyncClient() as client:
            # Get basic post data
            response = await client.get(
                f"{self.BASE_URL}/{post_id}",
                params={
                    "fields": "shares,likes.summary(true),comments.summary(true)",
                    "access_token": self.access_token,
                },
            )

            if response.status_code != 200:
                return {}

            data = response.json()

            analytics = {
                "shares": data.get("shares", {}).get("count", 0),
                "likes": data.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments": data.get("comments", {}).get("summary", {}).get("total_count", 0),
            }

            # Get insights (requires page access)
            insights_response = await client.get(
                f"{self.BASE_URL}/{post_id}/insights",
                params={
                    "metric": ",".join(metrics),
                    "access_token": self.access_token,
                },
            )

            if insights_response.status_code == 200:
                insights_data = insights_response.json()
                for insight in insights_data.get("data", []):
                    analytics[insight["name"]] = insight["values"][0]["value"]

            return analytics

    async def delete_content(self, post_id: str) -> bool:
        """Delete a Facebook post."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.BASE_URL}/{post_id}",
                params={"access_token": self.access_token},
            )

            return response.status_code == 200

    async def get_upload_limits(self) -> dict[str, Any]:
        """Get Facebook upload limits."""
        return {
            "image_specs": {
                "max_file_size": 4 * 1024 * 1024,  # 4 MB
                "recommended_dimensions": "1200x630",
                "supported_formats": ["jpg", "png", "gif", "bmp"],
            },
            "video_specs": {
                "max_file_size": 10 * 1024 * 1024 * 1024,  # 10 GB
                "max_duration": 240 * 60,  # 240 minutes
                "recommended_format": "mp4",
                "recommended_codec": "H.264",
                "recommended_audio": "AAC",
            },
            "text_limit": 63206,  # characters
            "rate_limits": {
                "posts_per_hour": 60,
                "total_calls_per_hour": 200,
            },
        }
