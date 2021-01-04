from api.models.dgraph import Dgraph

from api.models.auth import User, require_user
from api.models.person import ChildrenModel, People, PeopleDict, Person
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

router = APIRouter()


@router.get('/me',
            tags=['Me'],
            summary='Get userinfo',
            description='This is the first landing endpoint',
            response_model=Person)
async def me(request: Request, user: User = Depends(require_user)):
    dg = Dgraph()
    person = await dg.get_me(user)
    return person


@router.get("/people", tags=['People'], summary='Get list of all person', description='', response_model=PeopleDict)
async def people(request: Request, user: User = Depends(require_user)):
    dg = Dgraph()
    people = dg.get_people()
    return people


@router.post("/people/search", tags=['People'], summary='Search for person', description='', response_model=People)
async def search_people(request: Request, person: Person, user: User = Depends(require_user)):
    dg = Dgraph()
    people = dg.search_people(person)
    return people


@router.post("/people", tags=['People'], summary='Create list people', description='', response_model=PeopleDict)
async def create_people(request: Request, people: PeopleDict, user: User = Depends(require_user)):
    dg = Dgraph()
    dg.create_people(people)
    return people


@router.get("/people/{name}", tags=['People'], summary='Search person by email', description='', response_model=Person)
async def person(request: Request, name: str, user: User = Depends(require_user)):
    dg = Dgraph()
    person = dg.get_person(name)
    return person


@router.get("/people/{name}/children",
            tags=['People'],
            summary='Get Children of the person by email',
            description='',
            response_model=PeopleDict)
async def children(request: Request, name: str, user: User = Depends(require_user)):
    dg = Dgraph()
    children = dg.get_children(name)
    return children


@router.post("/people/{name}/children",
             tags=['People'],
             summary='Update children of the person by email',
             description='',
             response_model=PeopleDict)
async def update_children(request: Request, name: str, children: ChildrenModel, user: User = Depends(require_user)):
    dg = Dgraph()
    updated_children = dg.get_updated_children(name, children)
    return {"children": updated_children['children']}


@router.get("/people/{name}/parents",
            tags=['People'],
            summary='Get parents of the person by email',
            description='',
            response_model=PeopleDict)
async def parents(request: Request, name: str, user: User = Depends(require_user)):
    dg = Dgraph()
    parents = dg.get_parents(name)
    return parents


@router.get("/people/{name}/partners",
            tags=['People'],
            summary='Get partners of person by email',
            description='',
            response_model=PeopleDict)
async def partners(request: Request, name: str, user: User = Depends(require_user)):
    dg = Dgraph()
    partners = dg.get_partners(name)
    return partners


@router.post("/people/{name}/partners",
             tags=['People'],
             summary='Update partners of person by email',
             description='',
             response_model=PeopleDict)
async def update_partners(request: Request, name: str, partners: PeopleDict, user: User = Depends(require_user)):
    dg = Dgraph()
    partners = dg.update_partners(name, partners)
    return partners


@router.patch("/people/{name}", tags=['People'], summary='Upate person by email', description='', response_model=Person)
async def update_person(request: Request, person: Person, name: str, user: User = Depends(require_user)):
    if name != person.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='modifying name key is not allowed')
    if person.partners or person.children:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Please use '/{name}/partners' or '/{name}/children' endpoints to update relations")
    dg = Dgraph()
    updated_person = dg.update_person(name, person)
    return updated_person


@router.delete("/people/{name}",
               tags=['People'],
               summary='Delete person by email',
               description='',
               response_model=Person)
async def delete_person(request: Request, name: str, user: User = Depends(require_user)):
    dg = Dgraph()
    deleted_person = dg.delete_person(name)
    return deleted_person


# These endpoints are for debug purposes
# @router.get("/deleteme", response_model=Person)
# async def deleteme(request: Request, user: User = Depends(require_user)):
#     client = DgraphClient()
#     return client.delete_user(user)


@router.get("/deleteall", response_model=Person)
async def deleteall(request: Request, user: User = Depends(require_user)):
    dg = Dgraph()
    return dg.delete_all()
