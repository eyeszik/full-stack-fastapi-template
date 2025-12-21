"""Base class for social media platform integrations."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
import uuid

from app.models import PlatformType, SocialAccount


class BasePlatformIntegration(ABC):
    """Abstract base class for platform integrations using official APIs."""

    def __init__(self, social_account: SocialAccount):
        """Initialize with a social account containing credentials.

        Args:
            social_account: SocialAccount model with access tokens
        """
        self.social_account = social_account
        self.access_token = social_account.access_token
        self.refresh_token = social_account.refresh_token
        self.platform = social_account.platform

    @abstractmethod
    async def refresh_access_token(self) -> str:
        """Refresh the access token using the refresh token.

        Returns:
            New access token

        Raises:
            Exception: If token refresh fails
        """
        pass

    @abstractmethod
    async def verify_credentials(self) -> dict[str, Any]:
        """Verify that the credentials are valid.

        Returns:
            User/account info from the platform

        Raises:
            Exception: If credentials are invalid
        """
        pass

    @abstractmethod
    async def publish_content(
        self,
        content_data: dict[str, Any],
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Publish content to the platform.

        Args:
            content_data: Platform-specific content data
            media_urls: Optional list of media URLs to include

        Returns:
            Response containing post ID and URL

        Raises:
            Exception: If publishing fails
        """
        pass

    @abstractmethod
    async def schedule_content(
        self,
        content_data: dict[str, Any],
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Schedule content for future publishing.

        Args:
            content_data: Platform-specific content data
            scheduled_time: When to publish
            media_urls: Optional list of media URLs

        Returns:
            Response containing scheduled post info

        Raises:
            Exception: If scheduling fails
        """
        pass

    @abstractmethod
    async def get_analytics(
        self,
        post_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch analytics for a published post.

        Args:
            post_id: Platform-specific post ID
            metrics: List of metrics to fetch (None = all available)

        Returns:
            Dictionary of metric name -> value

        Raises:
            Exception: If analytics fetch fails
        """
        pass

    @abstractmethod
    async def delete_content(self, post_id: str) -> bool:
        """Delete a published post.

        Args:
            post_id: Platform-specific post ID

        Returns:
            True if deletion successful

        Raises:
            Exception: If deletion fails
        """
        pass

    @abstractmethod
    async def get_upload_limits(self) -> dict[str, Any]:
        """Get platform-specific upload limits and requirements.

        Returns:
            Dictionary with limit information:
            - max_file_size
            - max_video_duration
            - supported_formats
            - rate_limits
        """
        pass

    def _check_token_expiry(self) -> bool:
        """Check if access token is expired or close to expiry.

        Returns:
            True if token needs refresh
        """
        if not self.social_account.token_expires_at:
            return False

        # Refresh if less than 5 minutes remaining
        time_until_expiry = (
            self.social_account.token_expires_at - datetime.utcnow()
        ).total_seconds()

        return time_until_expiry < 300  # 5 minutes

    async def ensure_valid_token(self) -> None:
        """Ensure access token is valid, refresh if needed."""
        if self._check_token_expiry():
            new_token = await self.refresh_access_token()
            self.access_token = new_token
            # Note: Caller should update the database with new token


class IntegrationError(Exception):
    """Base exception for integration errors."""

    def __init__(self, message: str, platform: PlatformType, status_code: int | None = None):
        self.platform = platform
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(IntegrationError):
    """Raised when authentication fails."""
    pass


class RateLimitError(IntegrationError):
    """Raised when rate limit is exceeded."""
    pass


class ContentValidationError(IntegrationError):
    """Raised when content doesn't meet platform requirements."""
    pass
