"""Factory for creating platform integration instances."""

from app.models import PlatformType, SocialAccount
from app.services.integrations.base import BasePlatformIntegration
from app.services.integrations.youtube import YouTubeIntegration
from app.services.integrations.twitter import TwitterIntegration
from app.services.integrations.facebook import FacebookIntegration
from app.services.integrations.instagram import InstagramIntegration
from app.services.integrations.linkedin import LinkedInIntegration
from app.core.config import settings


class IntegrationFactory:
    """Factory to create platform-specific integration instances."""

    @staticmethod
    def create(
        social_account: SocialAccount,
        **kwargs,
    ) -> BasePlatformIntegration:
        """Create integration instance for a platform.

        Args:
            social_account: SocialAccount with credentials
            **kwargs: Platform-specific configuration

        Returns:
            Platform integration instance

        Raises:
            ValueError: If platform not supported
        """
        platform = social_account.platform

        if platform == PlatformType.YOUTUBE:
            return YouTubeIntegration(
                social_account=social_account,
                client_secret=kwargs.get("client_secret") or settings.YOUTUBE_CLIENT_SECRET,
            )

        elif platform == PlatformType.TWITTER:
            return TwitterIntegration(social_account=social_account)

        elif platform == PlatformType.FACEBOOK:
            return FacebookIntegration(
                social_account=social_account,
                app_secret=kwargs.get("app_secret") or settings.FACEBOOK_APP_SECRET,
            )

        elif platform == PlatformType.INSTAGRAM:
            return InstagramIntegration(
                social_account=social_account,
                instagram_account_id=kwargs.get("instagram_account_id") or social_account.account_handle,
            )

        elif platform == PlatformType.LINKEDIN:
            return LinkedInIntegration(
                social_account=social_account,
                client_secret=kwargs.get("client_secret") or settings.LINKEDIN_CLIENT_SECRET,
                person_urn=kwargs.get("person_urn") or social_account.account_handle,
            )

        else:
            raise ValueError(f"Unsupported platform: {platform}")


# Convenience functions for common operations
async def publish_to_platform(
    social_account: SocialAccount,
    content_data: dict,
    media_urls: list[str] | None = None,
) -> dict:
    """Publish content to a platform.

    Args:
        social_account: SocialAccount with credentials
        content_data: Platform-specific content data
        media_urls: Optional media URLs

    Returns:
        Publication result
    """
    integration = IntegrationFactory.create(social_account)
    return await integration.publish_content(content_data, media_urls)


async def fetch_platform_analytics(
    social_account: SocialAccount,
    post_id: str,
    metrics: list[str] | None = None,
) -> dict:
    """Fetch analytics for a post.

    Args:
        social_account: SocialAccount with credentials
        post_id: Platform-specific post ID
        metrics: Optional list of metrics to fetch

    Returns:
        Analytics data
    """
    integration = IntegrationFactory.create(social_account)
    return await integration.get_analytics(post_id, metrics)


async def verify_platform_credentials(social_account: SocialAccount) -> dict:
    """Verify that platform credentials are valid.

    Args:
        social_account: SocialAccount to verify

    Returns:
        Account information from platform
    """
    integration = IntegrationFactory.create(social_account)
    return await integration.verify_credentials()
