"""
A/B Testing Statistical Analysis Service

Provides statistical analysis for A/B tests using scipy, including:
- Two-proportion z-test for statistical significance
- Wilson score confidence intervals
- Cohen's h effect size calculation
- Automatic winner declaration based on statistical thresholds
"""

import uuid
from datetime import datetime
from typing import Any

import numpy as np
from scipy import stats
from sqlmodel import Session, select

from app.models import (
    ABTest,
    ABTestGoal,
    ABTestResult,
    ABTestStatus,
    ABTestVariant,
    ContentAnalytics,
    ContentVariant,
)


class ABTestAnalyzer:
    """Statistical analyzer for A/B tests with scipy-based calculations."""

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def calculate_p_value(
        metric_a: int, total_a: int, metric_b: int, total_b: int
    ) -> float:
        """
        Calculate p-value using two-proportion z-test.

        Args:
            metric_a: Success count for variant A (e.g., engagements)
            total_a: Total count for variant A (e.g., views)
            metric_b: Success count for variant B
            total_b: Total count for variant B

        Returns:
            p-value (0.0 to 1.0), where < 0.05 indicates statistical significance
        """
        if total_a == 0 or total_b == 0:
            return 1.0

        p_a = metric_a / total_a
        p_b = metric_b / total_b
        p_pooled = (metric_a + metric_b) / (total_a + total_b)

        # Standard error of difference in proportions
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1 / total_a + 1 / total_b))

        if se == 0:
            return 1.0

        # Z-statistic
        z = (p_a - p_b) / se

        # Two-tailed p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        return float(p_value)

    @staticmethod
    def calculate_wilson_confidence_interval(
        successes: int, total: int, confidence_level: float = 0.95
    ) -> tuple[float, float]:
        """
        Calculate Wilson score confidence interval for a proportion.

        More accurate than normal approximation for small sample sizes.

        Args:
            successes: Number of successes
            total: Total number of trials
            confidence_level: Confidence level (default 0.95 for 95%)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if total == 0:
            return (0.0, 0.0)

        p = successes / total
        z = stats.norm.ppf(1 - (1 - confidence_level) / 2)
        z_squared = z * z

        denominator = 1 + z_squared / total
        center = (p + z_squared / (2 * total)) / denominator
        margin = (z * np.sqrt(p * (1 - p) / total + z_squared / (4 * total * total))) / denominator

        return (float(max(0, center - margin)), float(min(1, center + margin)))

    @staticmethod
    def calculate_effect_size(
        metric_a: int, total_a: int, metric_b: int, total_b: int
    ) -> float:
        """
        Calculate Cohen's h effect size for proportions.

        Effect size interpretation:
        - Small: 0.2
        - Medium: 0.5
        - Large: 0.8

        Args:
            metric_a: Success count for variant A
            total_a: Total count for variant A
            metric_b: Success count for variant B
            total_b: Total count for variant B

        Returns:
            Effect size (Cohen's h)
        """
        if total_a == 0 or total_b == 0:
            return 0.0

        p_a = metric_a / total_a
        p_b = metric_b / total_b

        # Cohen's h = 2 * (arcsin(sqrt(p1)) - arcsin(sqrt(p2)))
        h = 2 * (np.arcsin(np.sqrt(p_a)) - np.arcsin(np.sqrt(p_b)))

        return float(abs(h))

    def get_variant_metrics(
        self, variant_id: uuid.UUID, goal: ABTestGoal
    ) -> tuple[int, int]:
        """
        Extract relevant metrics from content variant analytics.

        Args:
            variant_id: Content variant ID
            goal: A/B test goal type

        Returns:
            Tuple of (metric_value, total_views)
        """
        # Get the most recent analytics for this variant
        analytics_stmt = (
            select(ContentAnalytics)
            .join(ContentVariant)
            .where(ContentVariant.id == variant_id)
            .order_by(ContentAnalytics.fetched_at.desc())
        )
        analytics = self.session.exec(analytics_stmt).first()

        if not analytics:
            return (0, 0)

        metrics: dict[str, Any] = analytics.metrics

        # Extract total views/impressions
        total_views = (
            metrics.get("views", 0)
            or metrics.get("impressions", 0)
            or metrics.get("reach", 0)
        )

        # Extract goal-specific metric
        if goal == ABTestGoal.ENGAGEMENT_RATE:
            engagement = (
                metrics.get("likes", 0)
                + metrics.get("comments", 0)
                + metrics.get("shares", 0)
                + metrics.get("saves", 0)
            )
            return (engagement, total_views)

        elif goal == ABTestGoal.CLICK_THROUGH_RATE:
            clicks = metrics.get("clicks", 0) or metrics.get("link_clicks", 0)
            return (clicks, total_views)

        elif goal == ABTestGoal.CONVERSION_RATE:
            conversions = metrics.get("conversions", 0)
            return (conversions, total_views)

        elif goal == ABTestGoal.REACH:
            reach = metrics.get("reach", 0) or metrics.get("unique_viewers", 0)
            return (reach, total_views)

        elif goal == ABTestGoal.WATCH_TIME:
            watch_time = metrics.get("watch_time", 0)
            return (watch_time, total_views)

        return (0, total_views)

    async def analyze_test(self, ab_test_id: uuid.UUID) -> ABTestResult | None:
        """
        Analyze an A/B test and calculate statistical results.

        Args:
            ab_test_id: A/B test ID

        Returns:
            ABTestResult with statistical calculations, or None if insufficient data
        """
        # Get the test
        test = self.session.get(ABTest, ab_test_id)
        if not test:
            return None

        # Get test variants (expecting exactly 2)
        variants_stmt = select(ABTestVariant).where(
            ABTestVariant.ab_test_id == ab_test_id
        )
        variants = list(self.session.exec(variants_stmt).all())

        if len(variants) != 2:
            return None

        variant_a, variant_b = variants[0], variants[1]

        # Get metrics for each variant
        metric_a, total_a = self.get_variant_metrics(
            variant_a.content_variant_id, test.goal
        )
        metric_b, total_b = self.get_variant_metrics(
            variant_b.content_variant_id, test.goal
        )

        # Calculate statistical measures
        p_value = self.calculate_p_value(metric_a, total_a, metric_b, total_b)
        effect_size = self.calculate_effect_size(metric_a, total_a, metric_b, total_b)

        # Determine statistical significance
        min_sample_reached = (
            total_a >= test.min_sample_size and total_b >= test.min_sample_size
        )
        alpha = 1 - test.confidence_level
        is_significant = p_value < alpha and min_sample_reached

        # Calculate confidence intervals for better variant
        if total_a > 0 and total_b > 0:
            rate_a = metric_a / total_a
            rate_b = metric_b / total_b
            better_variant_id = (
                variant_a.content_variant_id if rate_a > rate_b else variant_b.content_variant_id
            )
            better_metric = metric_a if rate_a > rate_b else metric_b
            better_total = total_a if rate_a > rate_b else total_b

            ci_lower, ci_upper = self.calculate_wilson_confidence_interval(
                better_metric, better_total, test.confidence_level
            )
        else:
            ci_lower, ci_upper = 0.0, 0.0

        # Create or update result
        result_stmt = select(ABTestResult).where(
            ABTestResult.ab_test_id == ab_test_id
        )
        existing_result = self.session.exec(result_stmt).first()

        if existing_result:
            existing_result.variant_a_views = total_a
            existing_result.variant_a_engagement = metric_a
            existing_result.variant_b_views = total_b
            existing_result.variant_b_engagement = metric_b
            existing_result.p_value = p_value
            existing_result.statistical_significance = is_significant
            existing_result.effect_size = effect_size
            existing_result.confidence_interval_lower = ci_lower
            existing_result.confidence_interval_upper = ci_upper
            existing_result.calculated_at = datetime.utcnow()
            self.session.add(existing_result)
            result = existing_result
        else:
            result = ABTestResult(
                ab_test_id=ab_test_id,
                variant_a_id=variant_a.content_variant_id,
                variant_b_id=variant_b.content_variant_id,
                variant_a_views=total_a,
                variant_a_engagement=metric_a,
                variant_b_views=total_b,
                variant_b_engagement=metric_b,
                p_value=p_value,
                statistical_significance=is_significant,
                effect_size=effect_size,
                confidence_interval_lower=ci_lower,
                confidence_interval_upper=ci_upper,
            )
            self.session.add(result)

        # Auto-declare winner if significant
        if is_significant and test.status == ABTestStatus.RUNNING:
            if total_a > 0 and total_b > 0:
                rate_a = metric_a / total_a
                rate_b = metric_b / total_b
                winner_id = (
                    variant_a.content_variant_id if rate_a > rate_b else variant_b.content_variant_id
                )
                test.winner_variant_id = winner_id
                test.status = ABTestStatus.COMPLETED
                test.completed_at = datetime.utcnow()
                self.session.add(test)

        self.session.commit()
        self.session.refresh(result)

        return result

    async def get_test_summary(self, ab_test_id: uuid.UUID) -> dict[str, Any]:
        """
        Get a comprehensive summary of an A/B test with human-readable results.

        Args:
            ab_test_id: A/B test ID

        Returns:
            Dictionary with test summary including winner, confidence, and recommendations
        """
        test = self.session.get(ABTest, ab_test_id)
        if not test:
            return {"error": "Test not found"}

        result = await self.analyze_test(ab_test_id)
        if not result:
            return {"error": "Insufficient data for analysis"}

        # Calculate rates
        rate_a = (
            result.variant_a_engagement / result.variant_a_views
            if result.variant_a_views > 0
            else 0
        )
        rate_b = (
            result.variant_b_engagement / result.variant_b_views
            if result.variant_b_views > 0
            else 0
        )

        # Determine winner
        if result.statistical_significance:
            winner = "Variant A" if rate_a > rate_b else "Variant B"
            improvement = abs(rate_a - rate_b) / min(rate_a, rate_b) * 100 if min(rate_a, rate_b) > 0 else 0
        else:
            winner = "No clear winner yet"
            improvement = 0

        # Effect size interpretation
        if result.effect_size and result.effect_size < 0.2:
            effect_interpretation = "Small"
        elif result.effect_size and result.effect_size < 0.5:
            effect_interpretation = "Medium"
        elif result.effect_size and result.effect_size >= 0.5:
            effect_interpretation = "Large"
        else:
            effect_interpretation = "Unknown"

        return {
            "test_id": str(ab_test_id),
            "test_name": test.name,
            "status": test.status,
            "goal": test.goal,
            "variant_a": {
                "views": result.variant_a_views,
                "metric": result.variant_a_engagement,
                "rate": round(rate_a, 4),
            },
            "variant_b": {
                "views": result.variant_b_views,
                "metric": result.variant_b_engagement,
                "rate": round(rate_b, 4),
            },
            "statistical_analysis": {
                "p_value": round(result.p_value, 6) if result.p_value else None,
                "is_significant": result.statistical_significance,
                "confidence_level": test.confidence_level,
                "effect_size": round(result.effect_size, 4) if result.effect_size else None,
                "effect_interpretation": effect_interpretation,
                "confidence_interval": (
                    f"[{result.confidence_interval_lower:.4f}, {result.confidence_interval_upper:.4f}]"
                    if result.confidence_interval_lower
                    else None
                ),
            },
            "conclusion": {
                "winner": winner,
                "improvement_percentage": round(improvement, 2) if improvement else 0,
                "sample_size_sufficient": (
                    result.variant_a_views >= test.min_sample_size
                    and result.variant_b_views >= test.min_sample_size
                ),
                "recommendation": (
                    f"Deploy {winner} - statistically significant improvement detected"
                    if result.statistical_significance
                    else "Continue testing - need more data for statistical significance"
                ),
            },
        }
