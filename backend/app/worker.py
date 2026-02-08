"""Celery worker for background tasks and scheduled jobs."""

from celery import Celery
from celery.schedules import crontab
from datetime import datetime
import logging

from app.core.config import settings
from app.core.db import engine
from sqlmodel import Session
from app.services.scheduler import ContentScheduler
from app.services.analytics_aggregator import AnalyticsAggregator
from app import crud

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "content_automation",
    broker=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:6379/0",
    backend=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:6379/0",
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# =============================================================================
# SCHEDULED TASKS
# =============================================================================

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Configure periodic tasks."""

    # Process scheduled posts every minute
    sender.add_periodic_task(
        60.0,  # Every 60 seconds
        process_scheduled_posts.s(),
        name="process_scheduled_posts",
    )

    # Fetch analytics every hour
    sender.add_periodic_task(
        crontab(minute=0),  # Every hour
        fetch_analytics_batch.s(),
        name="fetch_analytics_hourly",
    )

    # Database cleanup daily at 2 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        cleanup_old_data.s(),
        name="cleanup_daily",
    )

    # Backup database daily at 3 AM
    sender.add_periodic_task(
        crontab(hour=3, minute=0),
        backup_database.s(),
        name="backup_daily",
    )

    # Analyze running A/B tests every hour
    sender.add_periodic_task(
        crontab(minute=30),  # Every hour at :30
        analyze_running_ab_tests.s(),
        name="analyze_ab_tests_hourly",
    )


# =============================================================================
# CONTENT PUBLISHING TASKS
# =============================================================================

@celery_app.task(bind=True, max_retries=3)
def process_scheduled_posts(self):
    """Process all posts scheduled for current time.

    Runs every minute via Celery Beat.
    """
    import asyncio
    try:
        with Session(engine) as session:
            scheduler = ContentScheduler(session)
            results = asyncio.run(scheduler.process_scheduled_posts())

            logger.info(
                f"[CELERY] Processed {len(results)} scheduled posts",
                extra={"count": len(results), "results": results}
            )

            return {
                "success": True,
                "processed": len(results),
                "results": results,
            }

    except Exception as e:
        logger.error(f"[CELERY ERROR] Failed to process scheduled posts: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute


@celery_app.task(bind=True, max_retries=3)
def publish_content_variant(self, variant_id: str, immediate: bool = True):
    """Publish a single content variant.

    Args:
        variant_id: UUID of content variant
        immediate: Publish now or queue for scheduled time
    """
    import asyncio
    try:
        with Session(engine) as session:
            variant = crud.get_content_variant(session=session, variant_id=variant_id)
            if not variant:
                return {"error": "Variant not found"}

            scheduler = ContentScheduler(session)
            result = asyncio.run(scheduler.schedule_variant(variant, immediate=immediate))

            logger.info(
                f"[CELERY] Published variant {variant_id}",
                extra={"variant_id": variant_id, "result": result}
            )

            return result

    except Exception as e:
        logger.error(f"[CELERY ERROR] Failed to publish variant {variant_id}: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


# =============================================================================
# ANALYTICS TASKS
# =============================================================================

@celery_app.task(bind=True)
def fetch_analytics_batch(self):
    """Fetch analytics for all published variants.

    Runs hourly via Celery Beat.
    """
    import asyncio
    try:
        with Session(engine) as session:
            # Get all published variants from last 30 days
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            statement = select(ContentVariant).where(
                ContentVariant.published_at.isnot(None),
                ContentVariant.published_at >= cutoff_date,
            )
            variants = session.exec(statement).all()

            aggregator = AnalyticsAggregator(session)
            results = []

            for variant in variants:
                try:
                    result = asyncio.run(aggregator.fetch_and_store_analytics(str(variant.id)))
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to fetch analytics for {variant.id}: {e}")

            logger.info(
                f"[CELERY] Fetched analytics for {len(results)} variants",
                extra={"count": len(results)}
            )

            return {
                "success": True,
                "fetched": len(results),
            }

    except Exception as e:
        logger.error(f"[CELERY ERROR] Analytics batch failed: {e}")
        return {"error": str(e)}


@celery_app.task(bind=True, max_retries=3)
def fetch_variant_analytics(self, variant_id: str):
    """Fetch analytics for a single variant.

    Args:
        variant_id: UUID of content variant
    """
    import asyncio
    try:
        with Session(engine) as session:
            aggregator = AnalyticsAggregator(session)
            result = asyncio.run(aggregator.fetch_and_store_analytics(variant_id))

            logger.info(
                f"[CELERY] Fetched analytics for variant {variant_id}",
                extra={"variant_id": variant_id, "result": result}
            )

            return result

    except Exception as e:
        logger.error(f"[CELERY ERROR] Failed to fetch analytics: {e}")
        raise self.retry(exc=e, countdown=600)  # Retry after 10 minutes


# =============================================================================
# MAINTENANCE TASKS
# =============================================================================

@celery_app.task
def cleanup_old_data(self):
    """Clean up old analytics and temporary data.

    Runs daily at 2 AM via Celery Beat.
    """
    try:
        with Session(engine) as session:
            from datetime import timedelta

            # Delete analytics older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            statement = delete(ContentAnalytics).where(
                ContentAnalytics.fetched_at < cutoff_date
            )
            result = session.exec(statement)
            session.commit()

            logger.info(
                f"[CELERY] Cleaned up {result.rowcount} old analytics records",
                extra={"deleted": result.rowcount}
            )

            return {
                "success": True,
                "deleted_analytics": result.rowcount,
            }

    except Exception as e:
        logger.error(f"[CELERY ERROR] Cleanup failed: {e}")
        return {"error": str(e)}


@celery_app.task
def backup_database(self):
    """Backup database to S3.

    Runs daily at 3 AM via Celery Beat.
    """
    import subprocess
    from datetime import datetime

    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/backups/db_backup_{timestamp}.sql.gz"

        # Create PostgreSQL dump
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_SERVER,
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "|", "gzip", ">", backup_file
        ]

        subprocess.run(" ".join(cmd), shell=True, check=True)

        # Upload to S3 if configured
        if settings.AWS_ACCESS_KEY_ID and settings.S3_BACKUP_BUCKET:
            import boto3
            s3 = boto3.client('s3')
            s3.upload_file(
                backup_file,
                settings.S3_BACKUP_BUCKET,
                f"database-backups/db_backup_{timestamp}.sql.gz"
            )

            logger.info(
                f"[CELERY] Database backed up to S3",
                extra={"backup_file": backup_file}
            )

        return {
            "success": True,
            "backup_file": backup_file,
        }

    except Exception as e:
        logger.error(f"[CELERY ERROR] Backup failed: {e}")
        return {"error": str(e)}


# =============================================================================
# AI CONTENT GENERATION TASKS
# =============================================================================

@celery_app.task(bind=True, max_retries=2)
def generate_ai_caption(self, content_id: str, platform: str):
    """Generate AI caption for content.

    Args:
        content_id: UUID of content
        platform: Target platform
    """
    import asyncio
    try:
        from app.services.ai_assistant import AIContentAssistant

        with Session(engine) as session:
            content = crud.get_content(session=session, content_id=content_id)
            if not content:
                return {"error": "Content not found"}

            assistant = AIContentAssistant(provider="openai")
            result = asyncio.run(assistant.generate_caption(
                content_type=content.content_type.value,
                platform=platform,
                topic=content.title,
                tone="professional",
            ))

            logger.info(
                f"[CELERY] Generated AI caption for content {content_id}",
                extra={"content_id": content_id, "platform": platform}
            )

            return result

    except Exception as e:
        logger.error(f"[CELERY ERROR] AI caption generation failed: {e}")
        raise self.retry(exc=e, countdown=120)


# =============================================================================
# A/B TESTING TASKS
# =============================================================================

@celery_app.task(bind=True)
def analyze_running_ab_tests(self):
    """Analyze all running A/B tests and update results.

    Runs hourly via Celery Beat. Calculates statistical significance,
    effect sizes, and auto-declares winners when thresholds are met.
    """
    import asyncio
    from sqlmodel import select
    from app.models import ABTest, ABTestStatus
    from app.services.ab_testing import ABTestAnalyzer

    try:
        with Session(engine) as session:
            # Get all running A/B tests
            stmt = select(ABTest).where(ABTest.status == ABTestStatus.RUNNING)
            running_tests = session.exec(stmt).all()

            logger.info(
                f"[CELERY] Found {len(running_tests)} running A/B tests to analyze"
            )

            analyzer = ABTestAnalyzer(session)
            results = []

            for test in running_tests:
                try:
                    result = asyncio.run(analyzer.analyze_test(test.id))
                    if result:
                        results.append({
                            "test_id": str(test.id),
                            "test_name": test.name,
                            "p_value": result.p_value,
                            "is_significant": result.statistical_significance,
                        })

                        if result.statistical_significance:
                            logger.info(
                                f"[CELERY] A/B test '{test.name}' reached statistical significance!",
                                extra={
                                    "test_id": str(test.id),
                                    "p_value": result.p_value,
                                    "winner_id": str(test.winner_variant_id),
                                }
                            )
                except Exception as test_error:
                    logger.warning(
                        f"[CELERY] Failed to analyze test {test.id}: {test_error}"
                    )
                    continue

            return {
                "success": True,
                "analyzed": len(results),
                "results": results,
            }

    except Exception as e:
        logger.error(f"[CELERY ERROR] A/B test analysis batch failed: {e}")
        raise self.retry(exc=e, countdown=600)  # Retry after 10 minutes


@celery_app.task(bind=True, max_retries=3)
def analyze_single_ab_test(self, test_id: str):
    """Analyze a specific A/B test on-demand.

    Args:
        test_id: UUID of the A/B test to analyze
    """
    import asyncio
    import uuid
    from app.services.ab_testing import ABTestAnalyzer

    try:
        with Session(engine) as session:
            analyzer = ABTestAnalyzer(session)
            result = asyncio.run(analyzer.analyze_test(uuid.UUID(test_id)))

            if not result:
                return {"error": "Unable to analyze test - insufficient data"}

            logger.info(
                f"[CELERY] Analyzed A/B test {test_id}",
                extra={
                    "test_id": test_id,
                    "p_value": result.p_value,
                    "is_significant": result.statistical_significance,
                }
            )

            return {
                "success": True,
                "test_id": test_id,
                "p_value": result.p_value,
                "statistical_significance": result.statistical_significance,
                "effect_size": result.effect_size,
            }

    except Exception as e:
        logger.error(f"[CELERY ERROR] Failed to analyze A/B test {test_id}: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


# =============================================================================
# MONITORING TASKS
# =============================================================================

@celery_app.task
def health_check(self):
    """Health check task for monitoring."""
    try:
        with Session(engine) as session:
            # Simple database query to verify connection
            session.exec(select(1)).one()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"[CELERY ERROR] Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }
