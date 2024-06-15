from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy.future import select # type: ignore
from app.dependencies import get_current_user
from app.database import get_db
from ..models import User, Match
from ..schemas import UserResponse
from typing import List

router = APIRouter()


@router.get("/alerm/list", response_model=List[UserResponse])
async def get_matching_requests(
    current_user: User = Depends(get_current_user),  # 인증된 사용자
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(User)
        .join(Match, Match.requester_id == User.id)
        .where(Match.responder_id == current_user.id, Match.status == "waiting")
    )
    result = await db.execute(query)
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="No matching requests found")
    return users
