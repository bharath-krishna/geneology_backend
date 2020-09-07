from fastapi import APIRouter, Depends, Request

from models.auth import require_user
from models.users import UserInfo

router = APIRouter()


@router.get('/user')
async def user(user: UserInfo = Depends(require_user)):
    return user


@router.get('/test/{id}')
async def test(id: int):
    return {"response": id}


@router.get('/single')
async def single(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/get')
    return response


@router.get('/multi')
async def multi(request: Request, user: UserInfo = Depends(require_user)):
    responses = await request.app.client.gather_urls('get', ['http://httpbin.org/get'] * 1000)
    return {"responses": responses}


@router.get('/callback')
async def callback():
    return
