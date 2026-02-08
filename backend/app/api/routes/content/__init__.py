"""Content automation API routes."""

from fastapi import APIRouter

from app.api.routes.content import ab_tests, contents, social_accounts

content_router = APIRouter()

# Register content sub-routers
content_router.include_router(contents.router, prefix="/contents", tags=["contents"])
content_router.include_router(social_accounts.router, prefix="/social-accounts", tags=["social-accounts"])
content_router.include_router(ab_tests.router, prefix="/ab-tests", tags=["ab-tests"])
