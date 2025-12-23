"""CRUD operations for content automation models."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select, func

from app.models import (
    SocialAccount,
    SocialAccountCreate,
    SocialAccountUpdate,
    MediaAsset,
    MediaAssetCreate,
    MediaAssetUpdate,
    ContentTemplate,
    ContentTemplateCreate,
    ContentTemplateUpdate,
    Campaign,
    CampaignCreate,
    CampaignUpdate,
    Content,
    ContentCreate,
    ContentUpdate,
    ContentVariant,
    ContentVariantCreate,
    ContentVariantUpdate,
    ContentAnalytics,
    ContentAnalyticsCreate,
    ContentAnalyticsUpdate,
    ContentStatus,
)


# =============================================================================
# SOCIAL ACCOUNT CRUD
# =============================================================================

def create_social_account(
    *, session: Session, account_in: SocialAccountCreate, owner_id: uuid.UUID
) -> SocialAccount:
    """Create a new social media account connection."""
    db_obj = SocialAccount.model_validate(account_in, update={"owner_id": owner_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_social_account(*, session: Session, account_id: uuid.UUID) -> SocialAccount | None:
    """Get social account by ID."""
    return session.get(SocialAccount, account_id)


def get_social_accounts_by_owner(
    *, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[SocialAccount]:
    """Get all social accounts for a user."""
    statement = (
        select(SocialAccount)
        .where(SocialAccount.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_social_account(
    *, session: Session, db_account: SocialAccount, account_in: SocialAccountUpdate
) -> SocialAccount:
    """Update social account."""
    account_data = account_in.model_dump(exclude_unset=True)
    db_account.sqlmodel_update(account_data, update={"updated_at": datetime.utcnow()})
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


def delete_social_account(*, session: Session, account_id: uuid.UUID) -> bool:
    """Delete social account."""
    account = session.get(SocialAccount, account_id)
    if account:
        session.delete(account)
        session.commit()
        return True
    return False


# =============================================================================
# MEDIA ASSET CRUD
# =============================================================================

def create_media_asset(
    *, session: Session, asset_in: MediaAssetCreate, owner_id: uuid.UUID
) -> MediaAsset:
    """Create a new media asset."""
    db_obj = MediaAsset.model_validate(asset_in, update={"owner_id": owner_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_media_asset(*, session: Session, asset_id: uuid.UUID) -> MediaAsset | None:
    """Get media asset by ID."""
    return session.get(MediaAsset, asset_id)


def get_media_assets_by_owner(
    *,
    session: Session,
    owner_id: uuid.UUID,
    media_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[MediaAsset]:
    """Get all media assets for a user."""
    statement = select(MediaAsset).where(MediaAsset.owner_id == owner_id)
    if media_type:
        statement = statement.where(MediaAsset.media_type == media_type)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_media_asset(
    *, session: Session, db_asset: MediaAsset, asset_in: MediaAssetUpdate
) -> MediaAsset:
    """Update media asset."""
    asset_data = asset_in.model_dump(exclude_unset=True)
    db_asset.sqlmodel_update(asset_data, update={"updated_at": datetime.utcnow()})
    session.add(db_asset)
    session.commit()
    session.refresh(db_asset)
    return db_asset


def delete_media_asset(*, session: Session, asset_id: uuid.UUID) -> bool:
    """Delete media asset."""
    asset = session.get(MediaAsset, asset_id)
    if asset:
        session.delete(asset)
        session.commit()
        return True
    return False


# =============================================================================
# CONTENT TEMPLATE CRUD
# =============================================================================

def create_content_template(
    *, session: Session, template_in: ContentTemplateCreate, owner_id: uuid.UUID
) -> ContentTemplate:
    """Create a new content template."""
    db_obj = ContentTemplate.model_validate(template_in, update={"owner_id": owner_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_content_template(
    *, session: Session, template_id: uuid.UUID
) -> ContentTemplate | None:
    """Get content template by ID."""
    return session.get(ContentTemplate, template_id)


def get_content_templates_by_owner(
    *,
    session: Session,
    owner_id: uuid.UUID,
    platform: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[ContentTemplate]:
    """Get all content templates for a user."""
    statement = select(ContentTemplate).where(ContentTemplate.owner_id == owner_id)
    if platform:
        statement = statement.where(ContentTemplate.platform == platform)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_public_templates(
    *, session: Session, platform: str | None = None, skip: int = 0, limit: int = 100
) -> list[ContentTemplate]:
    """Get public templates shared by all users."""
    statement = select(ContentTemplate).where(ContentTemplate.is_public == True)
    if platform:
        statement = statement.where(ContentTemplate.platform == platform)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_content_template(
    *, session: Session, db_template: ContentTemplate, template_in: ContentTemplateUpdate
) -> ContentTemplate:
    """Update content template."""
    template_data = template_in.model_dump(exclude_unset=True)
    db_template.sqlmodel_update(template_data, update={"updated_at": datetime.utcnow()})
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template


def increment_template_usage(*, session: Session, template_id: uuid.UUID) -> None:
    """Increment template usage count."""
    template = session.get(ContentTemplate, template_id)
    if template:
        template.usage_count += 1
        session.add(template)
        session.commit()


# =============================================================================
# CAMPAIGN CRUD
# =============================================================================

def create_campaign(
    *, session: Session, campaign_in: CampaignCreate, owner_id: uuid.UUID
) -> Campaign:
    """Create a new campaign."""
    db_obj = Campaign.model_validate(campaign_in, update={"owner_id": owner_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_campaign(*, session: Session, campaign_id: uuid.UUID) -> Campaign | None:
    """Get campaign by ID."""
    return session.get(Campaign, campaign_id)


def get_campaigns_by_owner(
    *, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Campaign]:
    """Get all campaigns for a user."""
    statement = (
        select(Campaign)
        .where(Campaign.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_campaign(
    *, session: Session, db_campaign: Campaign, campaign_in: CampaignUpdate
) -> Campaign:
    """Update campaign."""
    campaign_data = campaign_in.model_dump(exclude_unset=True)
    db_campaign.sqlmodel_update(campaign_data, update={"updated_at": datetime.utcnow()})
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return db_campaign


# =============================================================================
# CONTENT CRUD
# =============================================================================

def create_content(
    *, session: Session, content_in: ContentCreate, owner_id: uuid.UUID
) -> Content:
    """Create a new content item."""
    db_obj = Content.model_validate(content_in, update={"owner_id": owner_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_content(*, session: Session, content_id: uuid.UUID) -> Content | None:
    """Get content by ID."""
    return session.get(Content, content_id)


def get_contents_by_owner(
    *,
    session: Session,
    owner_id: uuid.UUID,
    status: ContentStatus | None = None,
    campaign_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Content]:
    """Get all content items for a user."""
    statement = select(Content).where(Content.owner_id == owner_id)
    if status:
        statement = statement.where(Content.status == status)
    if campaign_id:
        statement = statement.where(Content.campaign_id == campaign_id)
    statement = statement.offset(skip).limit(limit).order_by(Content.created_at.desc())
    return list(session.exec(statement).all())


def update_content(
    *, session: Session, db_content: Content, content_in: ContentUpdate
) -> Content:
    """Update content item."""
    content_data = content_in.model_dump(exclude_unset=True)
    db_content.sqlmodel_update(content_data, update={"updated_at": datetime.utcnow()})
    session.add(db_content)
    session.commit()
    session.refresh(db_content)
    return db_content


def update_content_status(
    *, session: Session, content_id: uuid.UUID, status: ContentStatus
) -> Content | None:
    """Update content status."""
    content = session.get(Content, content_id)
    if content:
        content.status = status
        content.updated_at = datetime.utcnow()
        if status == ContentStatus.PUBLISHED:
            content.published_at = datetime.utcnow()
        session.add(content)
        session.commit()
        session.refresh(content)
    return content


# =============================================================================
# CONTENT VARIANT CRUD
# =============================================================================

def create_content_variant(
    *, session: Session, variant_in: ContentVariantCreate
) -> ContentVariant:
    """Create a new content variant for a platform."""
    db_obj = ContentVariant.model_validate(variant_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_content_variant(
    *, session: Session, variant_id: uuid.UUID
) -> ContentVariant | None:
    """Get content variant by ID."""
    return session.get(ContentVariant, variant_id)


def get_variants_by_content(
    *, session: Session, content_id: uuid.UUID
) -> list[ContentVariant]:
    """Get all variants for a content item."""
    statement = select(ContentVariant).where(ContentVariant.content_id == content_id)
    return list(session.exec(statement).all())


def get_scheduled_variants(
    *, session: Session, before: datetime | None = None
) -> list[ContentVariant]:
    """Get variants scheduled for publishing."""
    statement = select(ContentVariant).where(
        ContentVariant.scheduled_for.isnot(None),
        ContentVariant.published_at.is_(None),
    )
    if before:
        statement = statement.where(ContentVariant.scheduled_for <= before)
    return list(session.exec(statement).all())


def update_content_variant(
    *, session: Session, db_variant: ContentVariant, variant_in: ContentVariantUpdate
) -> ContentVariant:
    """Update content variant."""
    variant_data = variant_in.model_dump(exclude_unset=True)
    db_variant.sqlmodel_update(variant_data, update={"updated_at": datetime.utcnow()})
    session.add(db_variant)
    session.commit()
    session.refresh(db_variant)
    return db_variant


def mark_variant_published(
    *, session: Session, variant_id: uuid.UUID, platform_post_id: str, platform_url: str
) -> ContentVariant | None:
    """Mark variant as published."""
    variant = session.get(ContentVariant, variant_id)
    if variant:
        variant.published_at = datetime.utcnow()
        variant.platform_post_id = platform_post_id
        variant.platform_url = platform_url
        session.add(variant)
        session.commit()
        session.refresh(variant)
    return variant


# =============================================================================
# CONTENT ANALYTICS CRUD
# =============================================================================

def create_content_analytics(
    *, session: Session, analytics_in: ContentAnalyticsCreate
) -> ContentAnalytics:
    """Create a new analytics record."""
    db_obj = ContentAnalytics.model_validate(analytics_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_analytics_by_variant(
    *, session: Session, variant_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[ContentAnalytics]:
    """Get all analytics for a content variant."""
    statement = (
        select(ContentAnalytics)
        .where(ContentAnalytics.content_variant_id == variant_id)
        .order_by(ContentAnalytics.fetched_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_latest_analytics(
    *, session: Session, variant_id: uuid.UUID
) -> ContentAnalytics | None:
    """Get most recent analytics for a variant."""
    statement = (
        select(ContentAnalytics)
        .where(ContentAnalytics.content_variant_id == variant_id)
        .order_by(ContentAnalytics.fetched_at.desc())
        .limit(1)
    )
    return session.exec(statement).first()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_content_stats_by_owner(*, session: Session, owner_id: uuid.UUID) -> dict[str, Any]:
    """Get content statistics for a user."""
    total_content = session.exec(
        select(func.count(Content.id)).where(Content.owner_id == owner_id)
    ).one()

    published_content = session.exec(
        select(func.count(Content.id)).where(
            Content.owner_id == owner_id, Content.status == ContentStatus.PUBLISHED
        )
    ).one()

    draft_content = session.exec(
        select(func.count(Content.id)).where(
            Content.owner_id == owner_id, Content.status == ContentStatus.DRAFT
        )
    ).one()

    scheduled_content = session.exec(
        select(func.count(Content.id)).where(
            Content.owner_id == owner_id, Content.status == ContentStatus.SCHEDULED
        )
    ).one()

    return {
        "total": total_content,
        "published": published_content,
        "draft": draft_content,
        "scheduled": scheduled_content,
    }
