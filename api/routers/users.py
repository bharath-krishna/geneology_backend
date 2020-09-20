from fastapi import APIRouter, Depends, Request

from models.person import Person

router = APIRouter()


@router.get('/logout')
async def logout(request: Request, user: Person = Depends(Person.require_user)):
    return user


@router.get('/callback')
async def callback():
    return
