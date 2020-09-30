from typing import Dict, List

from api.models.auth import User, require_user
from api.models.person import ChildrenModel, Person
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

router = APIRouter()


@router.get('/me',
            tags=['Me'],
            summary='Get userinfo',
            description='This is the first landing endpoint',
            response_model=Person)
async def me(request: Request, user: User = Depends(require_user)):
    person = Person(**user.userinfo)
    await request.app.dg.sync_with_dgraph(person)
    return person


@router.get("/people",
            tags=['People'],
            summary='Get list of all person',
            description='',
            response_model=Dict[str, List[Person]])
async def people(request: Request, user: User = Depends(require_user)):
    client = request.app.dg
    people = client.query_all()
    return people


@router.post("/people",
             tags=['People'],
             summary='Create list people',
             description='',
             response_model=Dict[str, List[Person]])
async def create_people(request: Request, people: Dict[str, List[Person]], user: User = Depends(require_user)):
    client = request.app.dg
    for person in people["people"]:
        client.create_person(person)
    return people


@router.get("/people/{name}", tags=['People'], summary='Search person by email', description='', response_model=Person)
async def person(request: Request, name: str, user: User = Depends(require_user)):
    client = request.app.dg
    db_person = client.search_by_name(name)
    if not db_person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'person with name {name} not found')
    return db_person


@router.get("/people/{email}/children",
            tags=['People'],
            summary='Get Children of the person by email',
            description='',
            response_model=Dict[str, List[Person]])
async def children(request: Request, email: str, user: User = Depends(require_user)):
    client = request.app.dg
    children = client.get_children(email)
    return children


@router.post("/people/{email}/children",
             tags=['People'],
             summary='Update children of the person by email',
             description='',
             response_model=Dict[str, List[Person]])
async def update_children(request: Request, email: str, children: ChildrenModel, user: User = Depends(require_user)):
    client = request.app.dg
    updated_children = client.update_children(email, children.children)
    return {"children": updated_children['children']}


@router.get("/people/{name}/parents",
            tags=['People'],
            summary='Get parents of the person by email',
            description='',
            response_model=Dict[str, List[Person]])
async def parents(request: Request, name: str, user: User = Depends(require_user)):
    client = request.app.dg
    parents = client.get_parents(name)
    return parents


@router.get("/people/{name}/partners",
            tags=['People'],
            summary='Get partners of person by email',
            description='',
            response_model=Dict[str, List[Person]])
async def partners(request: Request, name: str, user: User = Depends(require_user)):
    client = request.app.dg
    partners = client.get_partners(name)
    return partners


@router.post("/people/{name}/partners",
             tags=['People'],
             summary='Update partners of person by email',
             description='',
             response_model=Dict[str, List[Person]])
async def update_partners(request: Request,
                          name: str,
                          partners: Dict[str, List[Person]],
                          user: User = Depends(require_user)):
    client = request.app.dg
    partners = client.update_partners(name, partners['partners'])
    return partners


@router.patch("/people/{name}", tags=['People'], summary='Upate person by email', description='', response_model=Person)
async def update_person(request: Request, person: Person, name: str, user: User = Depends(require_user)):
    if name != person.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'modifying name key is not allowed')
    if person.partners or person.children:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Please use '/{name}/partners' or '/{name}/children' endpoints to update relations")
    client = request.app.dg
    updated_person = client.update_person(name, person)
    return updated_person


@router.delete("/people/{name}",
               tags=['People'],
               summary='Delete person by email',
               description='',
               response_model=Person)
async def delete_person(request: Request, name: str, user: User = Depends(require_user)):
    client = request.app.dg
    deleted_person = client.delete_user(name)
    return deleted_person


# These endpoints are for debug purposes
# @router.get("/deleteme", response_model=Person)
# async def deleteme(request: Request, user: User = Depends(require_user)):
#     client = request.app.dg
#     return client.delete_user(user)


@router.get("/deleteall", response_model=Person)
async def deleteall(request: Request, user: User = Depends(require_user)):
    client = request.app.dg
    return client.delete_all()
