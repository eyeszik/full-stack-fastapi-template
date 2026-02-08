"""
A/B Testing API Endpoints

Provides endpoints for creating, managing, and analyzing A/B tests.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.api.deps import CurrentUser, get_session
from app.models import (
    ABTest,
    ABTestCreate,
    ABTestPublic,
    ABTestsPublic,
    ABTestUpdate,
    ABTestVariant,
    ABTestVariantCreate,
    ABTestVariantPublic,
    ABTestVariantsPublic,
    ABTestVariantUpdate,
    ABTestResult,
    ABTestResultPublic,
    ABTestResultsPublic,
    ABTestStatus,
    ContentVariant,
)
from app.services.ab_testing import ABTestAnalyzer

router = APIRouter()


@router.get("/", response_model=ABTestsPublic)
def read_ab_tests(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve A/B tests owned by the current user.
    """
    count_stmt = select(func.count()).select_from(ABTest).where(ABTest.owner_id == current_user.id)
    count = session.exec(count_stmt).one()

    stmt = (
        select(ABTest)
        .where(ABTest.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(ABTest.created_at.desc())
    )
    tests = session.exec(stmt).all()

    return ABTestsPublic(data=tests, count=count)


@router.get("/{test_id}", response_model=ABTestPublic)
def read_ab_test(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Get A/B test by ID.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return test


@router.post("/", response_model=ABTestPublic)
def create_ab_test(
    test_in: ABTestCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Create new A/B test.
    """
    test = ABTest.model_validate(test_in, update={"owner_id": current_user.id})
    session.add(test)
    session.commit()
    session.refresh(test)
    return test


@router.patch("/{test_id}", response_model=ABTestPublic)
def update_ab_test(
    test_id: uuid.UUID,
    test_in: ABTestUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Update an A/B test.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = test_in.model_dump(exclude_unset=True)
    test.sqlmodel_update(update_data)
    session.add(test)
    session.commit()
    session.refresh(test)
    return test


@router.delete("/{test_id}")
def delete_ab_test(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Delete an A/B test.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(test)
    session.commit()
    return {"message": "A/B test deleted successfully"}


# =============================================================================
# A/B TEST VARIANTS
# =============================================================================


@router.get("/{test_id}/variants", response_model=ABTestVariantsPublic)
def read_test_variants(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Get all variants for an A/B test.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    stmt = select(ABTestVariant).where(ABTestVariant.ab_test_id == test_id)
    variants = session.exec(stmt).all()

    return ABTestVariantsPublic(data=variants, count=len(variants))


@router.post("/{test_id}/variants", response_model=ABTestVariantPublic)
def create_test_variant(
    test_id: uuid.UUID,
    variant_in: ABTestVariantCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Add a variant to an A/B test.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Verify content variant exists and belongs to user
    content_variant = session.get(ContentVariant, variant_in.content_variant_id)
    if not content_variant:
        raise HTTPException(status_code=404, detail="Content variant not found")

    # Check if test already has 2 variants (maximum for A/B test)
    existing_count = session.exec(
        select(func.count()).select_from(ABTestVariant).where(ABTestVariant.ab_test_id == test_id)
    ).one()

    if existing_count >= 2:
        raise HTTPException(
            status_code=400,
            detail="A/B test already has 2 variants. Remove one before adding another.",
        )

    variant = ABTestVariant.model_validate(variant_in)
    session.add(variant)
    session.commit()
    session.refresh(variant)
    return variant


@router.patch("/{test_id}/variants/{variant_id}", response_model=ABTestVariantPublic)
def update_test_variant(
    test_id: uuid.UUID,
    variant_id: uuid.UUID,
    variant_in: ABTestVariantUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Update a test variant.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    variant = session.get(ABTestVariant, variant_id)
    if not variant or variant.ab_test_id != test_id:
        raise HTTPException(status_code=404, detail="Test variant not found")

    update_data = variant_in.model_dump(exclude_unset=True)
    variant.sqlmodel_update(update_data)
    session.add(variant)
    session.commit()
    session.refresh(variant)
    return variant


@router.delete("/{test_id}/variants/{variant_id}")
def delete_test_variant(
    test_id: uuid.UUID,
    variant_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Remove a variant from an A/B test.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    variant = session.get(ABTestVariant, variant_id)
    if not variant or variant.ab_test_id != test_id:
        raise HTTPException(status_code=404, detail="Test variant not found")

    session.delete(variant)
    session.commit()
    return {"message": "Test variant removed successfully"}


# =============================================================================
# A/B TEST ANALYSIS
# =============================================================================


@router.post("/{test_id}/analyze", response_model=ABTestResultPublic)
async def analyze_ab_test(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Trigger statistical analysis for an A/B test.

    Calculates p-value, effect size, and confidence intervals.
    Auto-declares winner if statistically significant.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    analyzer = ABTestAnalyzer(session)
    result = await analyzer.analyze_test(test_id)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to analyze test. Ensure test has exactly 2 variants with analytics data.",
        )

    return result


@router.get("/{test_id}/results", response_model=ABTestResultPublic)
def get_test_results(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Get the latest analysis results for an A/B test.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    stmt = (
        select(ABTestResult)
        .where(ABTestResult.ab_test_id == test_id)
        .order_by(ABTestResult.calculated_at.desc())
    )
    result = session.exec(stmt).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No analysis results found. Run analysis first.",
        )

    return result


@router.get("/{test_id}/summary")
async def get_test_summary(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Get a comprehensive, human-readable summary of the A/B test.

    Includes winner, confidence intervals, effect size interpretation,
    and actionable recommendations.
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    analyzer = ABTestAnalyzer(session)
    summary = await analyzer.get_test_summary(test_id)

    if "error" in summary:
        raise HTTPException(status_code=400, detail=summary["error"])

    return summary


@router.post("/{test_id}/start")
def start_ab_test(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Start an A/B test (change status to RUNNING).
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Verify test has exactly 2 variants
    variant_count = session.exec(
        select(func.count()).select_from(ABTestVariant).where(ABTestVariant.ab_test_id == test_id)
    ).one()

    if variant_count != 2:
        raise HTTPException(
            status_code=400,
            detail=f"A/B test must have exactly 2 variants to start. Currently has {variant_count}.",
        )

    test.status = ABTestStatus.RUNNING
    session.add(test)
    session.commit()
    session.refresh(test)
    return test


@router.post("/{test_id}/stop")
def stop_ab_test(
    test_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Stop an A/B test (change status to COMPLETED).
    """
    test = session.get(ABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    test.status = ABTestStatus.COMPLETED
    session.add(test)
    session.commit()
    session.refresh(test)
    return test
