"""API routes for social account management."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    SocialAccount,
    SocialAccountCreate,
    SocialAccountUpdate,
    SocialAccountsPublic,
    SocialAccountPublic,
    Message,
)
from app.services.integration_factory import verify_platform_credentials

router = APIRouter()


@router.get("/", response_model=SocialAccountsPublic)
def read_social_accounts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve social accounts.
    """
    accounts = crud.get_social_accounts_by_owner(
        session=session,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    count = len(accounts)
    return SocialAccountsPublic(data=accounts, count=count)


@router.get("/{id}", response_model=SocialAccountPublic)
def read_social_account(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get social account by ID.
    """
    account = crud.get_social_account(session=session, account_id=id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return account


@router.post("/", response_model=SocialAccountPublic)
async def create_social_account(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    account_in: SocialAccountCreate,
) -> Any:
    """
    Create new social account connection.
    """
    # Create account
    account = crud.create_social_account(
        session=session, account_in=account_in, owner_id=current_user.id
    )

    # Verify credentials (async)
    try:
        account_info = await verify_platform_credentials(account)
        # Update account with verified info
        account.account_name = account_info.get("name", account.account_name)
    except Exception as e:
        # If verification fails, mark as inactive but keep the account
        account.is_active = False
        session.add(account)
        session.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to verify credentials: {str(e)}"
        )

    return account


@router.put("/{id}", response_model=SocialAccountPublic)
def update_social_account(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    account_in: SocialAccountUpdate,
) -> Any:
    """
    Update social account.
    """
    account = crud.get_social_account(session=session, account_id=id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    account = crud.update_social_account(
        session=session, db_account=account, account_in=account_in
    )
    return account


@router.delete("/{id}")
def delete_social_account(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete social account.
    """
    account = crud.get_social_account(session=session, account_id=id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = crud.delete_social_account(session=session, account_id=id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete account")

    return Message(message="Social account deleted successfully")


@router.post("/{id}/verify")
async def verify_social_account(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Verify social account credentials.
    """
    account = crud.get_social_account(session=session, account_id=id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        account_info = await verify_platform_credentials(account)
        return {
            "verified": True,
            "account_info": account_info,
        }
    except Exception as e:
        return {
            "verified": False,
            "error": str(e),
        }
