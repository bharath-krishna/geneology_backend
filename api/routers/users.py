from fastapi import APIRouter, Depends, Request

from models.person import Person

router = APIRouter()


@router.get('/logout',
            tags=['Logout'],
            summary='Log user out',
            description='Invalidate token and clear any session/cookies')
async def logout(request: Request, user: Person = Depends(Person.require_user)):
    return user


@router.get('/callback',
            tags=['Callback'],
            summary='A placeholder endpoint',
            description='This endpoint is just a placeholder for the oauth2 redirection for docs and does nothing')
async def callback():
    return
