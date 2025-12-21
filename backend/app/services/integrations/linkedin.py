"""LinkedIn API integration for professional content sharing."""

from datetime import datetime
from typing import Any
import httpx
import base64

from app.models import PlatformType
from app.services.integrations.base import (
    BasePlatformIntegration,
    AuthenticationError,
    ContentValidationError,
    RateLimitError,
)


class LinkedInIntegration(BasePlatformIntegration):
    """LinkedIn API v2 integration.

    Requires:
    - LinkedIn Developer App
    - OAuth 2.0 with w_member_social scope
    - Person or Organization URN

    API Docs: https://learn.microsoft.com/en-us/linkedin/
    """

    BASE_URL = "https://api.linkedin.com/v2"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

    def __init__(self, social_account, client_secret: str, person_urn: str):
        """Initialize LinkedIn integration.

        Args:
            social_account: SocialAccount with LinkedIn credentials
            client_secret: LinkedIn App client secret
            person_urn: LinkedIn person URN (urn:li:person:XXXXX)
        """
        super().__init__(social_account)
        self.client_secret = client_secret
        self.person_urn = person_urn

    async def refresh_access_token(self) -> str:
        """Refresh LinkedIn OAuth 2.0 token.

        Returns:
            New access token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.social_account.account_handle,
                    "client_secret": self.client_secret,
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Failed to refresh LinkedIn token: {response.text}",
                    PlatformType.LINKEDIN,
                    response.status_code,
                )

            data = response.json()
            return data["access_token"]

    async def verify_credentials(self) -> dict[str, Any]:
        """Verify LinkedIn credentials by fetching user profile."""
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/me",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Invalid LinkedIn credentials: {response.text}",
                    PlatformType.LINKEDIN,
                    response.status_code,
                )

            data = response.json()
            return {
                "id": data["id"],
                "first_name": data.get("localizedFirstName", ""),
                "last_name": data.get("localizedLastName", ""),
            }

    async def publish_content(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Share content on LinkedIn.

        Args:
            content_data: Must include:
                - text: Post text (max 3000 chars)
                - title: Optional article title
                - article_url: Optional URL to share
                - media_assets: Optional list of uploaded media URNs

        Returns:
            {
                "post_id": str,
                "url": str
            }
        """
        await self.ensure_valid_token()

        if "text" not in content_data:
            raise ContentValidationError(
                "text is required for LinkedIn posts",
                PlatformType.LINKEDIN,
            )

        # Build UGC post payload
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content_data["text"][:3000]
                    },
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Add article/link if provided
        if content_data.get("article_url"):
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "originalUrl": content_data["article_url"],
                    "title": {
                        "text": content_data.get("title", "")
                    },
                }
            ]

        # Add images if provided
        if content_data.get("media_assets"):
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "media": asset_urn,
                }
                for asset_urn in content_data["media_assets"]
            ]

        # Post to LinkedIn
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/ugcPosts",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code == 429:
                raise RateLimitError(
                    "LinkedIn rate limit exceeded",
                    PlatformType.LINKEDIN,
                    429,
                )

            if response.status_code not in [200, 201]:
                raise ContentValidationError(
                    f"LinkedIn post failed: {response.text}",
                    PlatformType.LINKEDIN,
                    response.status_code,
                )

            # LinkedIn returns post URN in header
            post_id = response.headers.get("X-LinkedIn-Id") or response.json().get("id")

            return {
                "post_id": post_id,
                "url": f"https://www.linkedin.com/feed/update/{post_id}/",
            }

    async def upload_image(self, image_path: str) -> str:
        """Upload image to LinkedIn and return asset URN.

        Args:
            image_path: Path to image file

        Returns:
            LinkedIn asset URN
        """
        await self.ensure_valid_token()

        # Step 1: Register upload
        async with httpx.AsyncClient() as client:
            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": self.person_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            register_response = await client.post(
                f"{self.BASE_URL}/assets?action=registerUpload",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json",
                },
                json=register_payload,
            )

            if register_response.status_code != 200:
                raise ContentValidationError(
                    f"Image upload registration failed: {register_response.text}",
                    PlatformType.LINKEDIN,
                    register_response.status_code,
                )

            register_data = register_response.json()
            upload_url = register_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_urn = register_data["value"]["asset"]

            # Step 2: Upload image binary
            with open(image_path, "rb") as image_file:
                upload_response = await client.put(
                    upload_url,
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                    },
                    content=image_file.read(),
                )

                if upload_response.status_code not in [200, 201]:
                    raise ContentValidationError(
                        f"Image upload failed: {upload_response.text}",
                        PlatformType.LINKEDIN,
                        upload_response.status_code,
                    )

            return asset_urn

    async def schedule_content(
        self,
        content_data: dict[str, Any],
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Schedule LinkedIn post.

        Note: LinkedIn API doesn't support native scheduling.
        Use external scheduler or post immediately.
        """
        return {
            "scheduled_for": scheduled_time.isoformat(),
            "status": "pending",
            "message": "LinkedIn doesn't support native scheduling via API. Use third-party scheduler.",
        }

    async def get_analytics(
        self,
        post_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch LinkedIn analytics for a post.

        Requires r_organization_social or r_member_social_analytics scope.
        """
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/socialActions/{post_id}",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
            )

            if response.status_code != 200:
                return {}

            data = response.json()

            return {
                "likes": data.get("likesSummary", {}).get("totalLikes", 0),
                "comments": data.get("commentsSummary", {}).get("totalComments", 0),
                "shares": data.get("sharesSummary", {}).get("totalShares", 0),
                "impressions": data.get("impressionCount", 0),
                "clicks": data.get("clickCount", 0),
            }

    async def delete_content(self, post_id: str) -> bool:
        """Delete a LinkedIn post.

        Args:
            post_id: LinkedIn UGC post URN

        Returns:
            True if deletion successful
        """
        await self.ensure_valid_token()

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.BASE_URL}/ugcPosts/{post_id}",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
            )

            return response.status_code == 204

    async def get_upload_limits(self) -> dict[str, Any]:
        """Get LinkedIn upload specifications."""
        return {
            "text_limit": 3000,  # characters for post commentary
            "article_limit": 110000,  # characters for LinkedIn articles
            "image_specs": {
                "max_file_size": 5 * 1024 * 1024,  # 5 MB
                "supported_formats": ["jpg", "png", "gif"],
                "recommended_dimensions": "1200x627",
            },
            "video_specs": {
                "max_file_size": 5 * 1024 * 1024 * 1024,  # 5 GB
                "max_duration": 10 * 60,  # 10 minutes
                "supported_formats": ["mp4"],
                "min_dimensions": "256x144",
                "max_dimensions": "4096x2304",
            },
            "document_specs": {
                "max_file_size": 100 * 1024 * 1024,  # 100 MB
                "supported_formats": ["pdf", "doc", "docx", "ppt", "pptx"],
            },
            "rate_limits": {
                "posts_per_day": 100,
                "api_calls_per_day": 100000,
            },
        }
