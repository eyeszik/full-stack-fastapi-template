import uuid
from datetime import datetime
from enum import Enum

from pydantic import EmailStr, HttpUrl
from sqlmodel import Field, Relationship, SQLModel, Column, JSON
from typing import Any


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

    # Content automation relationships
    social_accounts: list["SocialAccount"] = Relationship(back_populates="owner", cascade_delete=True)
    media_assets: list["MediaAsset"] = Relationship(back_populates="owner", cascade_delete=True)
    content_templates: list["ContentTemplate"] = Relationship(back_populates="owner", cascade_delete=True)
    campaigns: list["Campaign"] = Relationship(back_populates="owner", cascade_delete=True)
    content_items: list["Content"] = Relationship(back_populates="owner", cascade_delete=True)
    ab_tests: list["ABTest"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# =============================================================================
# CONTENT AUTOMATION MODELS
# =============================================================================

# Enums for content automation
class PlatformType(str, Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    MEDIUM = "medium"
    SUBSTACK = "substack"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class ContentType(str, Enum):
    VIDEO = "video"
    BLOG = "blog"
    SOCIAL_POST = "social_post"
    IMAGE_POST = "image_post"
    STORY = "story"
    REEL = "reel"
    THREAD = "thread"


# =============================================================================
# SOCIAL ACCOUNT MODELS
# =============================================================================

class SocialAccountBase(SQLModel):
    platform: PlatformType
    account_name: str = Field(max_length=255)
    account_handle: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class SocialAccountCreate(SocialAccountBase):
    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None


class SocialAccountUpdate(SQLModel):
    account_name: str | None = Field(default=None, max_length=255)
    account_handle: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_expires_at: datetime | None = None


class SocialAccount(SocialAccountBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    access_token: str  # Encrypted in production
    refresh_token: str | None = None
    token_expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="social_accounts")
    content_variants: list["ContentVariant"] = Relationship(back_populates="social_account")


class SocialAccountPublic(SocialAccountBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    token_expires_at: datetime | None


class SocialAccountsPublic(SQLModel):
    data: list[SocialAccountPublic]
    count: int


# =============================================================================
# MEDIA ASSET MODELS
# =============================================================================

class MediaAssetBase(SQLModel):
    file_name: str = Field(max_length=255)
    media_type: MediaType
    file_size: int  # bytes
    mime_type: str = Field(max_length=100)
    width: int | None = None
    height: int | None = None
    duration: int | None = None  # seconds for video/audio
    alt_text: str | None = Field(default=None, max_length=500)
    tags: str | None = Field(default=None, max_length=500)  # Comma-separated


class MediaAssetCreate(MediaAssetBase):
    storage_url: str


class MediaAssetUpdate(SQLModel):
    file_name: str | None = Field(default=None, max_length=255)
    alt_text: str | None = Field(default=None, max_length=500)
    tags: str | None = Field(default=None, max_length=500)


class MediaAsset(MediaAssetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    storage_url: str  # Cloud storage URL (S3, GCS, etc.)
    thumbnail_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="media_assets")


class MediaAssetPublic(MediaAssetBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    storage_url: str
    thumbnail_url: str | None
    created_at: datetime


class MediaAssetsPublic(SQLModel):
    data: list[MediaAssetPublic]
    count: int


# =============================================================================
# CONTENT TEMPLATE MODELS
# =============================================================================

class ContentTemplateBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    platform: PlatformType
    content_type: ContentType
    template_content: dict[str, Any] = Field(sa_column=Column(JSON))
    # template_content structure:
    # {
    #   "title": "{{product_name}} - Amazing Features!",
    #   "description": "Check out {{product_name}}...",
    #   "hashtags": ["#{{category}}", "#newproduct"],
    #   "variables": ["product_name", "category"]
    # }


class ContentTemplateCreate(ContentTemplateBase):
    pass


class ContentTemplateUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    template_content: dict[str, Any] | None = None


class ContentTemplate(ContentTemplateBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    is_public: bool = False  # Share with other users
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="content_templates")


class ContentTemplatePublic(ContentTemplateBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    is_public: bool
    usage_count: int
    created_at: datetime


class ContentTemplatesPublic(SQLModel):
    data: list[ContentTemplatePublic]
    count: int


# =============================================================================
# CAMPAIGN MODELS
# =============================================================================

class CampaignBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    start_date: datetime | None = None
    end_date: datetime | None = None
    goal: str | None = Field(default=None, max_length=500)
    target_platforms: list[str] = Field(default=[], sa_column=Column(JSON))


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    start_date: datetime | None = None
    end_date: datetime | None = None
    goal: str | None = Field(default=None, max_length=500)
    target_platforms: list[str] | None = None


class Campaign(CampaignBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="campaigns")
    content_items: list["Content"] = Relationship(back_populates="campaign")


class CampaignPublic(CampaignBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime


class CampaignsPublic(SQLModel):
    data: list[CampaignPublic]
    count: int


# =============================================================================
# CONTENT MODELS
# =============================================================================

class ContentBase(SQLModel):
    title: str = Field(max_length=500)
    content_type: ContentType
    status: ContentStatus = ContentStatus.DRAFT
    body: str | None = None  # Main content (text, script, etc.)


class ContentCreate(ContentBase):
    campaign_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None
    media_asset_ids: list[uuid.UUID] = []
    content_metadata: dict[str, Any] = {}  # Renamed to avoid SQLModel attribute shadow


class ContentUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=500)
    status: ContentStatus | None = None
    body: str | None = None
    content_metadata: dict[str, Any] | None = None
    campaign_id: uuid.UUID | None = None


class Content(ContentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    campaign_id: uuid.UUID | None = Field(
        default=None, foreign_key="campaign.id", ondelete="SET NULL"
    )
    template_id: uuid.UUID | None = Field(
        default=None, foreign_key="contenttemplate.id", ondelete="SET NULL"
    )
    content_metadata: dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    # content_metadata can include: tags, category, target_audience, tone, style
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: datetime | None = None

    owner: User | None = Relationship(back_populates="content_items")
    campaign: Campaign | None = Relationship(back_populates="content_items")
    content_variants: list["ContentVariant"] = Relationship(back_populates="content", cascade_delete=True)


class ContentPublic(ContentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    campaign_id: uuid.UUID | None
    template_id: uuid.UUID | None
    content_metadata: dict[str, Any]
    created_at: datetime
    published_at: datetime | None


class ContentsPublic(SQLModel):
    data: list[ContentPublic]
    count: int


# =============================================================================
# CONTENT VARIANT MODELS (Platform-specific versions)
# =============================================================================

class ContentVariantBase(SQLModel):
    platform: PlatformType
    platform_specific_data: dict[str, Any] = Field(sa_column=Column(JSON))
    # Platform-specific fields:
    # YouTube: {"video_title", "description", "tags", "category", "thumbnail_url"}
    # Twitter: {"tweet_text", "media_ids", "reply_settings"}
    # Instagram: {"caption", "hashtags", "location", "tagged_users"}
    # etc.
    scheduled_for: datetime | None = None
    published_at: datetime | None = None
    platform_post_id: str | None = Field(default=None, max_length=255)
    platform_url: str | None = None


class ContentVariantCreate(ContentVariantBase):
    content_id: uuid.UUID
    social_account_id: uuid.UUID


class ContentVariantUpdate(SQLModel):
    platform_specific_data: dict[str, Any] | None = None
    scheduled_for: datetime | None = None
    platform_post_id: str | None = Field(default=None, max_length=255)
    platform_url: str | None = None
    published_at: datetime | None = None


class ContentVariant(ContentVariantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content_id: uuid.UUID = Field(
        foreign_key="content.id", nullable=False, ondelete="CASCADE"
    )
    social_account_id: uuid.UUID = Field(
        foreign_key="socialaccount.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    content: Content | None = Relationship(back_populates="content_variants")
    social_account: SocialAccount | None = Relationship(back_populates="content_variants")
    analytics: list["ContentAnalytics"] = Relationship(back_populates="content_variant", cascade_delete=True)


class ContentVariantPublic(ContentVariantBase):
    id: uuid.UUID
    content_id: uuid.UUID
    social_account_id: uuid.UUID
    created_at: datetime


class ContentVariantsPublic(SQLModel):
    data: list[ContentVariantPublic]
    count: int


# =============================================================================
# CONTENT ANALYTICS MODELS
# =============================================================================

class ContentAnalyticsBase(SQLModel):
    metrics: dict[str, Any] = Field(sa_column=Column(JSON))
    # Platform-specific metrics:
    # YouTube: {"views", "likes", "dislikes", "comments", "shares", "watch_time", "ctr"}
    # Twitter: {"impressions", "engagements", "likes", "retweets", "replies", "profile_clicks"}
    # Instagram: {"reach", "impressions", "likes", "comments", "saves", "shares", "profile_visits"}
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class ContentAnalyticsCreate(ContentAnalyticsBase):
    content_variant_id: uuid.UUID


class ContentAnalyticsUpdate(SQLModel):
    metrics: dict[str, Any] | None = None


class ContentAnalytics(ContentAnalyticsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content_variant_id: uuid.UUID = Field(
        foreign_key="contentvariant.id", nullable=False, ondelete="CASCADE"
    )

    content_variant: ContentVariant | None = Relationship(back_populates="analytics")


class ContentAnalyticsPublic(ContentAnalyticsBase):
    id: uuid.UUID
    content_variant_id: uuid.UUID


class ContentAnalyticsListPublic(SQLModel):
    data: list[ContentAnalyticsPublic]
    count: int


# =============================================================================
# A/B TESTING MODELS
# =============================================================================

class ABTestGoal(str, Enum):
    ENGAGEMENT_RATE = "engagement_rate"  # likes+comments / views
    CLICK_THROUGH_RATE = "click_through_rate"  # clicks / views
    CONVERSION_RATE = "conversion_rate"  # conversions / views
    REACH = "reach"  # total unique viewers
    WATCH_TIME = "watch_time"  # total watch time in seconds


class ABTestStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ABTestBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    goal: ABTestGoal
    confidence_level: float = 0.95  # 95% confidence by default
    min_sample_size: int = 100  # Minimum views/impressions before declaring winner
    status: ABTestStatus = ABTestStatus.DRAFT


class ABTestCreate(ABTestBase):
    pass


class ABTestUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    status: ABTestStatus | None = None
    winner_variant_id: uuid.UUID | None = None


class ABTest(ABTestBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    winner_variant_id: uuid.UUID | None = None  # Set when test completes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    owner: User | None = Relationship(back_populates="ab_tests")
    test_variants: list["ABTestVariant"] = Relationship(back_populates="ab_test", cascade_delete=True)
    test_results: list["ABTestResult"] = Relationship(back_populates="ab_test", cascade_delete=True)


class ABTestPublic(ABTestBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    winner_variant_id: uuid.UUID | None
    created_at: datetime
    completed_at: datetime | None


class ABTestsPublic(SQLModel):
    data: list[ABTestPublic]
    count: int


# =============================================================================
# A/B TEST VARIANT MODELS
# =============================================================================

class ABTestVariantBase(SQLModel):
    variant_name: str = Field(max_length=100)  # e.g., "Variant A", "Variant B"
    traffic_allocation: float = Field(default=0.5)  # 0.0 to 1.0, should sum to 1.0 across variants


class ABTestVariantCreate(ABTestVariantBase):
    ab_test_id: uuid.UUID
    content_variant_id: uuid.UUID


class ABTestVariantUpdate(SQLModel):
    variant_name: str | None = Field(default=None, max_length=100)
    traffic_allocation: float | None = None


class ABTestVariant(ABTestVariantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ab_test_id: uuid.UUID = Field(
        foreign_key="abtest.id", nullable=False, ondelete="CASCADE"
    )
    content_variant_id: uuid.UUID = Field(
        foreign_key="contentvariant.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    ab_test: ABTest | None = Relationship(back_populates="test_variants")
    content_variant: ContentVariant | None = Relationship()


class ABTestVariantPublic(ABTestVariantBase):
    id: uuid.UUID
    ab_test_id: uuid.UUID
    content_variant_id: uuid.UUID
    created_at: datetime


class ABTestVariantsPublic(SQLModel):
    data: list[ABTestVariantPublic]
    count: int


# =============================================================================
# A/B TEST RESULT MODELS
# =============================================================================

class ABTestResultBase(SQLModel):
    variant_a_id: uuid.UUID
    variant_b_id: uuid.UUID
    variant_a_views: int = 0
    variant_a_engagement: int = 0
    variant_b_views: int = 0
    variant_b_engagement: int = 0
    p_value: float | None = None
    statistical_significance: bool = False
    effect_size: float | None = None  # Cohen's h for proportions
    confidence_interval_lower: float | None = None
    confidence_interval_upper: float | None = None
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class ABTestResultCreate(ABTestResultBase):
    ab_test_id: uuid.UUID


class ABTestResultUpdate(SQLModel):
    variant_a_views: int | None = None
    variant_a_engagement: int | None = None
    variant_b_views: int | None = None
    variant_b_engagement: int | None = None
    p_value: float | None = None
    statistical_significance: bool | None = None
    effect_size: float | None = None


class ABTestResult(ABTestResultBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ab_test_id: uuid.UUID = Field(
        foreign_key="abtest.id", nullable=False, ondelete="CASCADE"
    )

    ab_test: ABTest | None = Relationship(back_populates="test_results")


class ABTestResultPublic(ABTestResultBase):
    id: uuid.UUID
    ab_test_id: uuid.UUID


class ABTestResultsPublic(SQLModel):
    data: list[ABTestResultPublic]
    count: int


# =============================================================================
# UPDATE USER MODEL TO INCLUDE NEW RELATIONSHIPS
# =============================================================================
