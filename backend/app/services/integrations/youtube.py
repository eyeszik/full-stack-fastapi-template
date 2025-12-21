"""YouTube Data API v3 integration using official Google API."""

from datetime import datetime, timedelta
from typing import Any
import httpx

from app.models import PlatformType
from app.services.integrations.base import (
    BasePlatformIntegration,
    AuthenticationError,
    ContentValidationError,
    RateLimitError,
)


class YouTubeIntegration(BasePlatformIntegration):
    """YouTube Data API v3 integration.

    Requires:
    - Google OAuth 2.0 credentials
    - YouTube Data API v3 enabled in Google Cloud Console
    - Scopes: youtube.upload, youtube.force-ssl

    API Docs: https://developers.google.com/youtube/v3
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"
    UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
    TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(self, social_account, client_secret: str):
        """Initialize YouTube integration.

        Args:
            social_account: SocialAccount with YouTube credentials
            client_secret: Google OAuth client secret
        """
        super().__init__(social_account)
        self.client_secret = client_secret

    async def refresh_access_token(self) -> str:
        """Refresh access token using Google OAuth2.

        Returns:
            New access token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.social_account.account_handle,  # Store client_id here
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to refresh token: {response.text}",
                    PlatformType.YOUTUBE,
                    response.status_code,
                )

            data = response.json()
            return data["access_token"]

    async def verify_credentials(self) -> dict[str, Any]:
        """Verify YouTube credentials by fetching channel info."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/channels",
                params={"part": "snippet,statistics", "mine": "true"},
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Invalid YouTube credentials: {response.text}",
                    PlatformType.YOUTUBE,
                    response.status_code,
                )

            data = response.json()
            if not data.get("items"):
                raise AuthenticationError(
                    "No YouTube channel found for this account",
                    PlatformType.YOUTUBE,
                )

            channel = data["items"][0]
            return {
                "channel_id": channel["id"],
                "title": channel["snippet"]["title"],
                "subscriber_count": channel["statistics"].get("subscriberCount", 0),
            }

    async def publish_content(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Upload and publish a video to YouTube.

        Args:
            content_data: Must include:
                - title: Video title (max 100 chars)
                - description: Video description (max 5000 chars)
                - tags: List of tags (optional)
                - category_id: YouTube category ID (optional, default: 22 = People & Blogs)
                - privacy_status: public, private, or unlisted (default: public)
                - video_file_path: Path to video file (required)
            media_urls: Not used for YouTube (videos uploaded via multipart)

        Returns:
            {
                "video_id": str,
                "url": str,
                "status": str
            }
        """
        await self.ensure_valid_token()

        # Validate required fields
        if "title" not in content_data:
            raise ContentValidationError(
                "title is required",
                PlatformType.YOUTUBE,
            )

        if "video_file_path" not in content_data:
            raise ContentValidationError(
                "video_file_path is required for YouTube upload",
                PlatformType.YOUTUBE,
            )

        # Prepare metadata
        metadata = {
            "snippet": {
                "title": content_data["title"][:100],
                "description": content_data.get("description", "")[:5000],
                "tags": content_data.get("tags", []),
                "categoryId": content_data.get("category_id", "22"),
            },
            "status": {
                "privacyStatus": content_data.get("privacy_status", "public"),
                "selfDeclaredMadeForKids": content_data.get("made_for_kids", False),
            },
        }

        # Note: Actual video upload requires resumable upload protocol
        # This is a simplified example - production would use google-api-python-client
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Read video file (in production, use streaming upload)
            with open(content_data["video_file_path"], "rb") as video_file:
                files = {"video": video_file}
                response = await client.post(
                    f"{self.UPLOAD_URL}?part=snippet,status",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=metadata,
                    # Note: Simplified - real implementation uses resumable upload
                )

            if response.status_code == 429:
                raise RateLimitError(
                    "YouTube upload quota exceeded",
                    PlatformType.YOUTUBE,
                    429,
                )

            if response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"Upload failed: {response.text}",
                    PlatformType.YOUTUBE,
                    response.status_code,
                )

            data = response.json()
            video_id = data["id"]

            return {
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "status": data["status"]["uploadStatus"],
            }

    async def schedule_content(
        self,
        content_data: dict[str, Any],
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Schedule a video for future publishing.

        YouTube allows scheduling by setting publishAt timestamp.
        """
        content_data["privacy_status"] = "private"  # Must be private initially
        content_data["publish_at"] = scheduled_time.isoformat() + "Z"

        result = await self.publish_content(content_data, media_urls)

        # Update video to set publish time
        async with httpx.AsyncClient() as client:
            await client.put(
                f"{self.BASE_URL}/videos",
                params={"part": "status"},
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "id": result["video_id"],
                    "status": {
                        "privacyStatus": "private",
                        "publishAt": content_data["publish_at"],
                    },
                },
            )

        return {
            **result,
            "scheduled_for": scheduled_time.isoformat(),
        }

    async def get_analytics(
        self,
        post_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch YouTube Analytics for a video.

        Note: Requires YouTube Analytics API (separate from Data API).
        """
        await self.ensure_valid_token()

        # Default metrics
        if not metrics:
            metrics = ["views", "likes", "comments", "shares", "estimatedMinutesWatched"]

        async with httpx.AsyncClient() as client:
            # Fetch basic stats from Data API
            response = await client.get(
                f"{self.BASE_URL}/videos",
                params={"part": "statistics", "id": post_id},
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            if response.status_code != 200:
                return {}

            data = response.json()
            if not data.get("items"):
                return {}

            stats = data["items"][0]["statistics"]

            return {
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "dislikes": int(stats.get("dislikeCount", 0)),  # Hidden by YouTube now
                "comments": int(stats.get("commentCount", 0)),
                "favorites": int(stats.get("favoriteCount", 0)),
            }

    async def delete_content(self, post_id: str) -> bool:
        """Delete a YouTube video."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.BASE_URL}/videos",
                params={"id": post_id},
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            return response.status_code == 204

    async def get_upload_limits(self) -> dict[str, Any]:
        """Get YouTube upload limits.

        Returns:
            Platform upload specifications
        """
        return {
            "max_file_size": 256 * 1024 * 1024 * 1024,  # 256 GB
            "max_video_duration": 12 * 3600,  # 12 hours (requires verification)
            "supported_formats": [
                ".mov", ".mpeg4", ".mp4", ".avi", ".wmv", ".mpegps",
                ".flv", ".3gpp", ".webm", ".dnxhr", ".prores", ".cineform", ".hevc"
            ],
            "thumbnail_specs": {
                "dimensions": "1280x720",
                "format": ["jpg", "png"],
                "max_size": 2 * 1024 * 1024,  # 2 MB
            },
            "rate_limits": {
                "daily_upload_limit": "Varies by account (typically 10-15 videos/day)",
                "quota_units_per_upload": 1600,
                "daily_quota": 10000,  # Default quota units
            },
        }

    async def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload a custom thumbnail for a video.

        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image

        Returns:
            True if upload successful
        """
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            with open(thumbnail_path, "rb") as thumb_file:
                response = await client.post(
                    f"{self.BASE_URL}/thumbnails/set",
                    params={"videoId": video_id},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    files={"thumbnail": thumb_file},
                )

            return response.status_code == 200
