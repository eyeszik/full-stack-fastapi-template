"""Instagram Graph API integration for Instagram Business/Creator accounts."""

from datetime import datetime
from typing import Any
import httpx
import time

from app.models import PlatformType
from app.services.integrations.base import (
    BasePlatformIntegration,
    AuthenticationError,
    ContentValidationError,
    RateLimitError,
)


class InstagramIntegration(BasePlatformIntegration):
    """Instagram Graph API integration.

    Requires:
    - Instagram Business or Creator account
    - Facebook Page connected to Instagram account
    - instagram_basic, instagram_content_publish permissions

    API Docs: https://developers.facebook.com/docs/instagram-api
    """

    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, social_account, instagram_account_id: str):
        """Initialize Instagram integration.

        Args:
            social_account: SocialAccount with Instagram credentials
            instagram_account_id: Instagram Business Account ID
        """
        super().__init__(social_account)
        self.instagram_account_id = instagram_account_id

    async def refresh_access_token(self) -> str:
        """Refresh Facebook/Instagram access token.

        Uses same token refresh as Facebook since Instagram uses FB auth.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": "app_id",
                    "client_secret": "app_secret",
                    "fb_exchange_token": self.access_token,
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to refresh Instagram token: {response.text}",
                    PlatformType.INSTAGRAM,
                    response.status_code,
                )

            data = response.json()
            return data["access_token"]

    async def verify_credentials(self) -> dict[str, Any]:
        """Verify Instagram Business account access."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{self.instagram_account_id}",
                params={
                    "fields": "id,username,name,profile_picture_url,followers_count,media_count",
                    "access_token": self.access_token,
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Invalid Instagram credentials: {response.text}",
                    PlatformType.INSTAGRAM,
                    response.status_code,
                )

            data = response.json()
            return {
                "account_id": data["id"],
                "username": data["username"],
                "name": data.get("name", ""),
                "followers_count": data.get("followers_count", 0),
                "media_count": data.get("media_count", 0),
            }

    async def publish_content(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Publish content to Instagram.

        Instagram requires a two-step process:
        1. Create media container
        2. Publish the container

        Args:
            content_data: Must include:
                - image_url OR video_url: URL to media file (must be publicly accessible)
                - caption: Post caption (max 2200 chars)
                - location_id: Optional location tag
                - user_tags: Optional list of user tags
                - is_carousel_item: Boolean for carousel posts

        Returns:
            {
                "media_id": str,
                "url": str
            }
        """
        await self.ensure_valid_token()

        # Step 1: Create media container
        container_id = await self._create_media_container(content_data, media_urls)

        # Step 2: Publish container
        result = await self._publish_media_container(container_id)

        return result

    async def _create_media_container(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> str:
        """Create Instagram media container.

        Returns:
            Container ID
        """
        payload = {
            "access_token": self.access_token,
        }

        # Determine media type
        if content_data.get("image_url") or (media_urls and not content_data.get("video_url")):
            # Image post
            media_url = content_data.get("image_url") or (media_urls[0] if media_urls else None)
            if not media_url:
                raise ContentValidationError(
                    "image_url or media_urls required",
                    PlatformType.INSTAGRAM,
                )
            payload["image_url"] = media_url

        elif content_data.get("video_url"):
            # Video post
            payload["video_url"] = content_data["video_url"]
            payload["media_type"] = "VIDEO"

            # Optional: thumbnail for video
            if content_data.get("thumbnail_url"):
                payload["thumb_offset"] = content_data.get("thumb_offset", 0)

        else:
            raise ContentValidationError(
                "Either image_url or video_url required",
                PlatformType.INSTAGRAM,
            )

        # Add caption
        if content_data.get("caption"):
            caption = content_data["caption"][:2200]  # Max 2200 chars
            payload["caption"] = caption

        # Add location
        if content_data.get("location_id"):
            payload["location_id"] = content_data["location_id"]

        # Add user tags
        if content_data.get("user_tags"):
            payload["user_tags"] = content_data["user_tags"]

        # Create container
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/{self.instagram_account_id}/media",
                data=payload,
            )

            if response.status_code == 429:
                raise RateLimitError(
                    "Instagram rate limit exceeded",
                    PlatformType.INSTAGRAM,
                    429,
                )

            if response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"Container creation failed: {response.text}",
                    PlatformType.INSTAGRAM,
                    response.status_code,
                )

            data = response.json()
            return data["id"]

    async def _publish_media_container(self, container_id: str) -> dict[str, Any]:
        """Publish a media container.

        Args:
            container_id: Container ID from create step

        Returns:
            Published media info
        """
        async with httpx.AsyncClient() as client:
            # Check container status first
            status_response = await client.get(
                f"{self.BASE_URL}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": self.access_token,
                },
            )

            if status_response.status_code == 200:
                status = status_response.json().get("status_code")
                if status == "IN_PROGRESS":
                    # Wait for processing to complete (videos especially)
                    time.sleep(5)

            # Publish container
            response = await client.post(
                f"{self.BASE_URL}/{self.instagram_account_id}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
            )

            if response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"Publishing failed: {response.text}",
                    PlatformType.INSTAGRAM,
                    response.status_code,
                )

            data = response.json()
            media_id = data["id"]

            return {
                "media_id": media_id,
                "url": f"https://www.instagram.com/p/{media_id}/",
            }

    async def publish_carousel(
        self,
        items: list[dict[str, Any]],
        caption: str,
    ) -> dict[str, Any]:
        """Publish a carousel post (multiple images/videos).

        Args:
            items: List of media items, each with image_url or video_url
            caption: Carousel caption

        Returns:
            Published carousel info
        """
        # Step 1: Create containers for each item
        item_ids = []
        for item in items:
            item["is_carousel_item"] = True
            container_id = await self._create_media_container(item, None)
            item_ids.append(container_id)

        # Step 2: Create carousel container
        async with httpx.AsyncClient() as client:
            carousel_response = await client.post(
                f"{self.BASE_URL}/{self.instagram_account_id}/media",
                data={
                    "media_type": "CAROUSEL",
                    "children": ",".join(item_ids),
                    "caption": caption[:2200],
                    "access_token": self.access_token,
                },
            )

            if carousel_response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"Carousel creation failed: {carousel_response.text}",
                    PlatformType.INSTAGRAM,
                    carousel_response.status_code,
                )

            carousel_data = carousel_response.json()
            carousel_id = carousel_data["id"]

        # Step 3: Publish carousel
        return await self._publish_media_container(carousel_id)

    async def publish_story(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Publish an Instagram Story.

        Args:
            content_data: Must include image_url or video_url

        Returns:
            Story media info
        """
        content_data["media_type"] = "STORIES"
        return await self.publish_content(content_data)

    async def schedule_content(
        self,
        content_data: dict[str, Any],
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Schedule Instagram content.

        Note: Instagram Graph API doesn't support native scheduling.
        Content must be published immediately or use third-party scheduler.
        """
        return {
            "scheduled_for": scheduled_time.isoformat(),
            "status": "pending",
            "message": "Instagram doesn't support native scheduling via API. Use Creator Studio or third-party tools.",
        }

    async def get_analytics(
        self,
        post_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch Instagram Insights for a media post.

        Requires instagram_manage_insights permission.
        """
        await self.ensure_valid_token()

        # Default metrics
        if not metrics:
            metrics = [
                "impressions",
                "reach",
                "engagement",
                "saved",
                "likes",
                "comments",
            ]

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{post_id}/insights",
                params={
                    "metric": ",".join(metrics),
                    "access_token": self.access_token,
                },
            )

            if response.status_code != 200:
                return {}

            data = response.json()
            analytics = {}

            for item in data.get("data", []):
                metric_name = item["name"]
                metric_value = item["values"][0]["value"]
                analytics[metric_name] = metric_value

            return analytics

    async def delete_content(self, post_id: str) -> bool:
        """Delete an Instagram post.

        Note: Only works for media published via API, not manual posts.
        """
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.BASE_URL}/{post_id}",
                params={"access_token": self.access_token},
            )

            return response.status_code == 200

    async def get_upload_limits(self) -> dict[str, Any]:
        """Get Instagram upload specifications."""
        return {
            "feed_post": {
                "image_specs": {
                    "aspect_ratio": "4:5 to 1.91:1",
                    "recommended_dimensions": "1080x1350",
                    "max_file_size": 8 * 1024 * 1024,  # 8 MB
                    "supported_formats": ["jpg", "png"],
                },
                "video_specs": {
                    "aspect_ratio": "4:5 to 1.91:1",
                    "recommended_dimensions": "1080x1350",
                    "max_file_size": 100 * 1024 * 1024,  # 100 MB
                    "max_duration": 60,  # seconds
                    "min_duration": 3,
                    "supported_formats": ["mp4", "mov"],
                },
                "caption_limit": 2200,
            },
            "story": {
                "dimensions": "1080x1920",
                "aspect_ratio": "9:16",
                "max_duration": 15,  # seconds
                "max_file_size": 100 * 1024 * 1024,
            },
            "carousel": {
                "max_items": 10,
                "specs": "Same as feed_post",
            },
            "rate_limits": {
                "posts_per_day": 25,  # API limit
                "hashtags_per_post": 30,
            },
        }
