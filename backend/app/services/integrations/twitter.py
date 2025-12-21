"""Twitter API v2 integration using official Twitter API."""

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


class TwitterIntegration(BasePlatformIntegration):
    """Twitter API v2 integration.

    Requires:
    - Twitter Developer Account
    - OAuth 2.0 or OAuth 1.0a credentials
    - Elevated or Enterprise access for certain features

    API Docs: https://developer.twitter.com/en/docs/twitter-api
    """

    BASE_URL = "https://api.twitter.com/2"
    UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
    AUTH_URL = "https://api.twitter.com/2/oauth2/token"

    async def refresh_access_token(self) -> str:
        """Refresh Twitter OAuth 2.0 access token.

        Returns:
            New access token
        """
        # Twitter OAuth 2.0 token refresh
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.AUTH_URL,
                data={
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                    "client_id": self.social_account.account_handle,
                },
                auth=(
                    self.social_account.account_handle,
                    # Client secret should be stored securely
                    "client_secret",
                ),
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to refresh Twitter token: {response.text}",
                    PlatformType.TWITTER,
                    response.status_code,
                )

            data = response.json()
            return data["access_token"]

    async def verify_credentials(self) -> dict[str, Any]:
        """Verify Twitter credentials by fetching user info."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/me",
                params={
                    "user.fields": "id,name,username,public_metrics,verified"
                },
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Invalid Twitter credentials: {response.text}",
                    PlatformType.TWITTER,
                    response.status_code,
                )

            data = response.json()
            user = data["data"]

            return {
                "user_id": user["id"],
                "username": user["username"],
                "name": user["name"],
                "followers_count": user["public_metrics"]["followers_count"],
                "verified": user.get("verified", False),
            }

    async def publish_content(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Post a tweet to Twitter.

        Args:
            content_data: Must include:
                - text: Tweet text (max 280 chars for basic, 4000 for Premium)
                - media_paths: Optional list of local media file paths
                - reply_settings: "everyone", "mentionedUsers", "following" (optional)
                - poll: Optional poll data
                - quote_tweet_id: Optional tweet ID to quote

        Returns:
            {
                "tweet_id": str,
                "url": str,
                "text": str
            }
        """
        await self.ensure_valid_token()

        if "text" not in content_data:
            raise ContentValidationError(
                "text is required for Twitter posts",
                PlatformType.TWITTER,
            )

        # Validate text length
        max_length = content_data.get("max_length", 280)
        if len(content_data["text"]) > max_length:
            raise ContentValidationError(
                f"Tweet text exceeds {max_length} characters",
                PlatformType.TWITTER,
            )

        # Upload media if provided
        media_ids = []
        if content_data.get("media_paths"):
            media_ids = await self._upload_media(content_data["media_paths"])

        # Prepare tweet payload
        payload = {
            "text": content_data["text"],
        }

        if media_ids:
            payload["media"] = {"media_ids": media_ids}

        if content_data.get("reply_settings"):
            payload["reply_settings"] = content_data["reply_settings"]

        if content_data.get("poll"):
            payload["poll"] = content_data["poll"]

        if content_data.get("quote_tweet_id"):
            payload["quote_tweet_id"] = content_data["quote_tweet_id"]

        # Post tweet
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/tweets",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code == 429:
                raise RateLimitError(
                    "Twitter rate limit exceeded",
                    PlatformType.TWITTER,
                    429,
                )

            if response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"Tweet failed: {response.text}",
                    PlatformType.TWITTER,
                    response.status_code,
                )

            data = response.json()
            tweet = data["data"]
            tweet_id = tweet["id"]

            return {
                "tweet_id": tweet_id,
                "url": f"https://twitter.com/{self.social_account.account_handle}/status/{tweet_id}",
                "text": tweet["text"],
            }

    async def _upload_media(self, media_paths: list[str]) -> list[str]:
        """Upload media files to Twitter.

        Args:
            media_paths: List of local file paths

        Returns:
            List of media IDs
        """
        media_ids = []

        async with httpx.AsyncClient(timeout=120.0) as client:
            for path in media_paths:
                with open(path, "rb") as media_file:
                    files = {"media": media_file}
                    response = await client.post(
                        self.UPLOAD_URL,
                        headers={"Authorization": f"Bearer {self.access_token}"},
                        files=files,
                    )

                    if response.status_code == 200:
                        media_ids.append(response.json()["media_id_string"])

        return media_ids

    async def schedule_content(
        self,
        content_data: dict[str, Any],
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Schedule a tweet for future posting.

        Note: Scheduling requires Twitter API Enterprise or third-party tools.
        This returns a placeholder as native scheduling is limited.
        """
        # Twitter API v2 doesn't support native scheduling in basic/elevated access
        # Options:
        # 1. Use Ads API (requires ads account)
        # 2. Use third-party scheduler
        # 3. Implement own queue/scheduler

        return {
            "scheduled_for": scheduled_time.isoformat(),
            "status": "pending",
            "message": "Twitter scheduling requires enterprise access or external scheduler",
        }

    async def get_analytics(
        self,
        post_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch Twitter analytics for a tweet.

        Requires elevated or enterprise access for detailed metrics.
        """
        await self.ensure_valid_token()

        # Default metrics
        metric_fields = [
            "public_metrics",  # likes, retweets, replies, quotes, impressions
            "non_public_metrics",  # url_link_clicks, profile_clicks (own tweets only)
            "organic_metrics",  # organic impressions, engagements
        ]

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/tweets/{post_id}",
                params={
                    "tweet.fields": ",".join(metric_fields),
                },
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            if response.status_code != 200:
                return {}

            data = response.json()
            tweet = data.get("data", {})

            # Combine all available metrics
            analytics = {}
            if "public_metrics" in tweet:
                analytics.update(tweet["public_metrics"])
            if "non_public_metrics" in tweet:
                analytics.update(tweet["non_public_metrics"])
            if "organic_metrics" in tweet:
                analytics.update(tweet["organic_metrics"])

            return analytics

    async def delete_content(self, post_id: str) -> bool:
        """Delete a tweet."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.BASE_URL}/tweets/{post_id}",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            return response.status_code == 200

    async def get_upload_limits(self) -> dict[str, Any]:
        """Get Twitter upload limits and specifications."""
        return {
            "text_limits": {
                "basic": 280,
                "premium": 4000,  # Twitter Blue/Premium
            },
            "media_limits": {
                "images_per_tweet": 4,
                "videos_per_tweet": 1,
                "gifs_per_tweet": 1,
            },
            "image_specs": {
                "max_file_size": 5 * 1024 * 1024,  # 5 MB
                "supported_formats": ["jpg", "png", "gif", "webp"],
                "max_dimensions": "4096x4096",
            },
            "video_specs": {
                "max_file_size": 512 * 1024 * 1024,  # 512 MB
                "max_duration": 140,  # seconds (2:20)
                "supported_formats": ["mp4", "mov"],
                "recommended_bitrate": "5000 kbps",
            },
            "rate_limits": {
                "tweets_per_day": 2400,  # Varies by account age/type
                "tweets_per_15_min": 300,
                "media_uploads_per_day": "Unlimited (within storage quota)",
            },
        }

    async def create_thread(self, tweets: list[str]) -> list[dict[str, Any]]:
        """Post a Twitter thread.

        Args:
            tweets: List of tweet texts

        Returns:
            List of tweet results
        """
        results = []
        previous_tweet_id = None

        for tweet_text in tweets:
            content_data = {
                "text": tweet_text,
            }

            if previous_tweet_id:
                content_data["reply"] = {
                    "in_reply_to_tweet_id": previous_tweet_id
                }

            result = await self.publish_content(content_data)
            results.append(result)
            previous_tweet_id = result["tweet_id"]

        return results
