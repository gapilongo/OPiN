

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.user import user
from app.models.user import User
from app.core.security import get_current_active_user, get_current_active_superuser

router = APIRouter()

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: UUID,
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_superuser),
    soft_delete: bool = True
) -> Any:
    """
    Delete user.
    Only superusers can delete other users.
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves"
        )
    
    if soft_delete:
        deleted_user = await user.soft_delete(db=db, id=user_id)
    else:
        deleted_user = await user.delete(db=db, id=user_id)
    
    if not deleted_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return deleted_user

@router.delete("/bulk/delete", response_model=dict[UUID, bool])
async def bulk_delete_users(
    user_ids: List[UUID],
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_superuser),
    soft_delete: bool = True
) -> Any:
    """
    Bulk delete users.
    Only superusers can perform bulk deletions.
    Returns a dictionary mapping user IDs to deletion success status.
    """
    if any(id == current_user.id for id in user_ids):
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves"
        )
    
    results = await user.bulk_delete(
        db=db,
        ids=user_ids,
        soft=soft_delete
    )
    
    return results

@router.delete("/{user_id}/with-data")
async def remove_user_with_data(
    user_id: UUID,
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Completely remove a user and all related data.
    This is a dangerous operation and should only be used when absolutely necessary.
    Only superusers can perform this operation.
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves"
        )
    
    try:
        success = await user.remove_with_related_data(db=db, id=user_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        return {"message": "User and all related data successfully removed"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error removing user and related data: {str(e)}"
        )