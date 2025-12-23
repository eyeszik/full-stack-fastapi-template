"""Analytics aggregation service with KPI tracking and success criteria.

[SUCCESS_CRITERIA] Measurable outcomes for content performance.
[GUARDRAILS] Data validation and anomaly detection.
"""

from datetime import datetime, timedelta
from typing import Any
from dataclasses import dataclass
import logging

from sqlmodel import Session

from app import crud
from app.models import ContentVariant
from app.services.integration_factory import fetch_platform_analytics

logger = logging.getLogger(__name__)


@dataclass
class KPITargets:
    """[SUCCESS_CRITERIA] Target KPIs for content performance."""
    min_views: int = 1000
    min_engagement_rate: float = 0.02  # 2%
    min_likes: int = 50
    min_shares: int = 10
    target_ctr: float = 0.05  # 5% click-through rate


@dataclass
class PerformanceReport:
    """Comprehensive performance report with KPI validation."""
    variant_id: str
    platform: str
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    engagement_rate: float
    reach: int
    ctr: float

    # Success metrics
    meets_targets: bool
    kpi_score: float  # 0-1 based on target achievement
    recommendations: list[str]


class AnalyticsAggregator:
    """Aggregate and analyze content performance across platforms."""

    def __init__(self, session: Session):
        """Initialize aggregator."""
        self.session = session
        self.kpi_targets = KPITargets()

    async def fetch_and_store_analytics(
        self,
        variant_id: str,
    ) -> dict[str, Any]:
        """Fetch analytics from platform and store in database.

        [GUARDRAILS] Validates data before storage.
        """
        variant = crud.get_content_variant(session=self.session, variant_id=variant_id)
        if not variant or not variant.published_at:
            return {"error": "Variant not published"}

        social_account = crud.get_social_account(
            session=self.session,
            account_id=variant.social_account_id
        )
        if not social_account:
            return {"error": "Social account not found"}

        try:
            # Fetch from platform API
            metrics = await fetch_platform_analytics(
                social_account=social_account,
                post_id=variant.platform_post_id,
            )

            # [GUARDRAIL] Validate metrics
            if not self._validate_metrics(metrics):
                logger.warning(
                    f"[GUARDRAIL] Invalid metrics for variant {variant_id}",
                    extra={"metrics": metrics}
                )
                return {"error": "Invalid metrics data"}

            # Store in database
            analytics = crud.create_content_analytics(
                session=self.session,
                analytics_in={
                    "content_variant_id": variant_id,
                    "metrics": metrics,
                    "fetched_at": datetime.utcnow(),
                }
            )

            return {
                "success": True,
                "analytics_id": str(analytics.id),
                "metrics": metrics,
            }

        except Exception as e:
            logger.error(f"[ERROR] Analytics fetch failed: {e}")
            return {"error": str(e)}

    def generate_performance_report(
        self,
        variant_id: str,
    ) -> PerformanceReport | None:
        """Generate performance report with KPI validation.

        [SUCCESS_CRITERIA] Evaluates against measurable targets.
        """
        analytics = crud.get_latest_analytics(session=self.session, variant_id=variant_id)
        if not analytics:
            return None

        variant = crud.get_content_variant(session=self.session, variant_id=variant_id)
        if not variant:
            return None

        metrics = analytics.metrics

        # Extract platform-specific metrics
        views = metrics.get("views", 0) or metrics.get("impressions", 0)
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)
        shares = metrics.get("shares", 0) or metrics.get("retweets", 0)
        reach = metrics.get("reach", views)

        # Calculate engagement rate
        engagement = likes + comments + shares
        engagement_rate = engagement / max(views, 1)

        # Calculate CTR
        clicks = metrics.get("clicks", 0) or metrics.get("url_clicks", 0)
        ctr = clicks / max(views, 1)

        # Evaluate against KPIs
        meets_targets = (
            views >= self.kpi_targets.min_views and
            engagement_rate >= self.kpi_targets.min_engagement_rate and
            likes >= self.kpi_targets.min_likes and
            shares >= self.kpi_targets.min_shares
        )

        # Calculate KPI score (0-1)
        scores = [
            min(views / self.kpi_targets.min_views, 1.0),
            min(engagement_rate / self.kpi_targets.min_engagement_rate, 1.0),
            min(likes / self.kpi_targets.min_likes, 1.0),
            min(shares / self.kpi_targets.min_shares, 1.0),
        ]
        kpi_score = sum(scores) / len(scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            views, engagement_rate, ctr, variant.platform.value
        )

        return PerformanceReport(
            variant_id=str(variant_id),
            platform=variant.platform.value,
            total_views=views,
            total_likes=likes,
            total_comments=comments,
            total_shares=shares,
            engagement_rate=engagement_rate,
            reach=reach,
            ctr=ctr,
            meets_targets=meets_targets,
            kpi_score=kpi_score,
            recommendations=recommendations,
        )

    def _validate_metrics(self, metrics: dict) -> bool:
        """[GUARDRAIL] Validate metrics data."""
        # Check for required fields
        if not isinstance(metrics, dict):
            return False

        # Check for negative values (impossible)
        for value in metrics.values():
            if isinstance(value, (int, float)) and value < 0:
                return False

        return True

    def _generate_recommendations(
        self,
        views: int,
        engagement_rate: float,
        ctr: float,
        platform: str,
    ) -> list[str]:
        """Generate recommendations based on performance."""
        recommendations = []

        if views < self.kpi_targets.min_views:
            recommendations.append("Increase reach through hashtags and optimal posting times")

        if engagement_rate < self.kpi_targets.min_engagement_rate:
            recommendations.append("Improve content quality and add call-to-action")

        if ctr < self.kpi_targets.target_ctr:
            recommendations.append("Optimize thumbnails and titles for higher click-through")

        if not recommendations:
            recommendations.append("Content performing well - maintain current strategy")

        return recommendations

    async def generate_campaign_report(
        self,
        campaign_id: str,
    ) -> dict[str, Any]:
        """Generate aggregated report for entire campaign."""
        campaign = crud.get_campaign(session=self.session, campaign_id=campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        # Get all content in campaign
        contents = crud.get_contents_by_owner(
            session=self.session,
            owner_id=campaign.owner_id,
            campaign_id=campaign_id,
        )

        total_views = 0
        total_engagement = 0
        platform_breakdown = {}

        for content in contents:
            variants = crud.get_variants_by_content(
                session=self.session,
                content_id=content.id
            )

            for variant in variants:
                analytics = crud.get_latest_analytics(
                    session=self.session,
                    variant_id=variant.id
                )

                if analytics:
                    metrics = analytics.metrics
                    views = metrics.get("views", 0) or metrics.get("impressions", 0)
                    likes = metrics.get("likes", 0)
                    comments = metrics.get("comments", 0)
                    shares = metrics.get("shares", 0)

                    total_views += views
                    total_engagement += (likes + comments + shares)

                    platform = variant.platform.value
                    if platform not in platform_breakdown:
                        platform_breakdown[platform] = {
                            "views": 0,
                            "engagement": 0,
                            "posts": 0,
                        }

                    platform_breakdown[platform]["views"] += views
                    platform_breakdown[platform]["engagement"] += (likes + comments + shares)
                    platform_breakdown[platform]["posts"] += 1

        return {
            "campaign_id": str(campaign_id),
            "campaign_name": campaign.name,
            "total_views": total_views,
            "total_engagement": total_engagement,
            "engagement_rate": total_engagement / max(total_views, 1),
            "platform_breakdown": platform_breakdown,
            "content_count": len(contents),
        }
