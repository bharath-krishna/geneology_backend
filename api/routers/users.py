from typing import Dict

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


@router.get('/single', response_model=Dict)
async def single(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/get')
    return response


@router.get('/multi', response_model=Dict)
async def multi(request: Request, user: UserInfo = Depends(require_user)):
    responses = await request.app.client.gather_urls('get', ['http://httpbin.org/get'] * 1000)
    return {"responses": responses}


@router.get('/json', response_model=Dict)
async def json(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/json')
    return response


@router.get('/notfound', response_model=Dict)
async def notfound(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/jsdon')
    return response


@router.get('/connerr', response_model=Dict)
async def conerr(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpdbin.org/jsdon')
    return response


@router.get('/html', response_model=Dict)
async def html(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/html')
    return response


@router.get('/xml', response_model=Dict)
async def xml(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/xml')
    return response


@router.get('/unauth', response_model=Dict)
async def unauth(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/status/401')
    return response


@router.get('/created', response_model=Dict)
async def created(request: Request, user: UserInfo = Depends(require_user)):
    response = await request.app.client.call_url('get', 'http://httpbin.org/status/201', suppress_exceptions=True)
    return response


@router.get('/mixed', response_model=Dict)
async def mixed(request: Request, user: UserInfo = Depends(require_user)):
    urls = [
        'http://httpbin.org/get',
        'http://httpbin.org/json',
        'http://httpbin.org/html',
        'http://httpbin.org/xml',
        'http://httpbin.org/image',
        'http://httpbin.org/status/400',
        'http://httpbin.org/status/201',
        'http://httpbin.org/status/500',
        'http://httpbin.org/status/201',
        'http://httpbin.org/status/401',
    ]
    responses = await request.app.client.gather_urls('get', urls, return_exceptions=True)
    return {"responses": responses}


@router.get('/callback')
async def callback():
    return
