from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from models.person import Person

router = APIRouter()


@router.get('/me')
async def me(request: Request, user: Person = Depends(Person.require_user)):
    await request.app.dg.sync_with_dgraph(user)
    return user


@router.get("/people", response_model=Dict[str, List[Person]])
async def update_people(request: Request, user: Person = Depends(Person.require_user)):
    client = request.app.dg
    return client.query_all()


@router.get("/people/{email}", response_model=Person)
async def person(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    db_person = client.search_by_email(email)
    if not db_person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'person with email id {email} not found')
    return db_person


@router.get("/people/{email}/children", response_model=Dict[str, List[Person]])
async def children(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    children = client.get_children(email)
    return {"children": children}


@router.get("/people/{email}/parents", response_model=Dict[str, List[Person]])
async def parents(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    parents = client.get_parents(email)
    return {"parents": parents}


@router.get("/people/{email}/partners", response_model=Dict[str, List[Person]])
async def partners(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    partners = client.get_partners(email)
    return partners


@router.patch("/people/{email}", response_model=Person)
async def update_person(request: Request, person: Person, email: str, user: Person = Depends(Person.require_user)):
    if email != person.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'modifying email key is not allowed')
    client = request.app.dg
    updated_person = client.update_person(email, person)
    return updated_person


# These endpoints are for debug purposes
# @router.get("/deleteme", response_model=Person)
# async def deleteme(request: Request, user: Person = Depends(Person.require_user)):
#     client = request.app.dg
#     return client.delete_user(user)

# @router.get("/deleteall", response_model=Person)
# async def deleteall(request: Request, user: Person = Depends(Person.require_user)):
#     client = request.app.dg
#     return client.delete_all()
