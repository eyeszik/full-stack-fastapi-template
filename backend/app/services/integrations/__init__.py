"""Social media platform API integrations using official APIs."""

from app.services.integrations.base import BasePlatformIntegration
from app.services.integrations.youtube import YouTubeIntegration
from app.services.integrations.twitter import TwitterIntegration
from app.services.integrations.facebook import FacebookIntegration
from app.services.integrations.instagram import InstagramIntegration
from app.services.integrations.linkedin import LinkedInIntegration

__all__ = [
    "BasePlatformIntegration",
    "YouTubeIntegration",
    "TwitterIntegration",
    "FacebookIntegration",
    "InstagramIntegration",
    "LinkedInIntegration",
]
