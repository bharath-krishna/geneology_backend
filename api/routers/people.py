from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from models.person import Person

router = APIRouter()


@router.get('/me', tags=['Me'], summary='Get userinfo', description='This is the landing endpoint')
async def me(request: Request, user: Person = Depends(Person.require_user)):
    await request.app.dg.sync_with_dgraph(user)
    return user


@router.get("/people",
            tags=['People'],
            summary='Get list of all person',
            description='',
            response_model=Dict[str, List[Person]])
async def people(request: Request, user: Person = Depends(Person.require_user)):
    client = request.app.dg
    return client.query_all()


@router.post("/people",
             tags=['People'],
             summary='Create list people',
             description='',
             response_model=Dict[str, List[Person]])
async def create_people(request: Request, people: Dict[str, List[Person]], user: Person = Depends(Person.require_user)):
    client = request.app.dg
    for person in people["people"]:
        client.create_user(person)
    return people


@router.get("/people/{email}", tags=['People'], summary='Search person by email', description='', response_model=Person)
async def person(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    db_person = client.search_by_email(email)
    if not db_person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'person with email id {email} not found')
    return db_person


@router.get("/people/{email}/children",
            tags=['People'],
            summary='Get Children of the person by email',
            description='',
            response_model=Dict[str, List[Person]])
async def children(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    children = client.get_children(email)
    return {"children": children}


@router.get("/people/{email}/parents",
            tags=['People'],
            summary='Get parents of the person by email',
            description='',
            response_model=Dict[str, List[Person]])
async def parents(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    parents = client.get_parents(email)
    return {"parents": parents}


@router.get("/people/{email}/partners",
            tags=['People'],
            summary='Get partners of person by email',
            description='',
            response_model=Dict[str, List[Person]])
async def partners(request: Request, email: str, person: Person = Depends(Person.require_user)):
    client = request.app.dg
    partners = client.get_partners(email)
    return partners


@router.patch("/people/{email}",
              tags=['People'],
              summary='Upate person by email',
              description='',
              response_model=Person)
async def update_person(request: Request, person: Person, email: str, user: Person = Depends(Person.require_user)):
    if email != person.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'modifying email key is not allowed')
    client = request.app.dg
    updated_person = client.update_person(email, person)
    return updated_person


@router.delete("/people/{email}",
               tags=['People'],
               summary='Delete person by email',
               description='',
               response_model=Person)
async def delete_person(request: Request, email: str, user: Person = Depends(Person.require_user)):
    client = request.app.dg
    deleted_person = client.delete_user(email)
    return deleted_person


# These endpoints are for debug purposes
# @router.get("/deleteme", response_model=Person)
# async def deleteme(request: Request, user: Person = Depends(Person.require_user)):
#     client = request.app.dg
#     return client.delete_user(user)


@router.get("/deleteall", response_model=Person)
async def deleteall(request: Request, user: Person = Depends(Person.require_user)):
    client = request.app.dg
    return client.delete_all()
