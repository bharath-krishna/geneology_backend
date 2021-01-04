from api.models.auth import User, require_user
from fastapi import APIRouter, Depends, Request

router = APIRouter()


@router.get('/logout',
            tags=['Logout'],
            summary='Log user out',
            description='Invalidate token and clear any session/cookies')
async def logout(request: Request, user: User = Depends(require_user)):
    return user
