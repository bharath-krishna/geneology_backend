from api.models.auth import User
from fastapi import HTTPException, status
from api.dgraph.dgraph_client import get_client
from api.models.person import ChildrenModel, PeopleDict, Person


class Dgraph():
    def __init__(self):
        self.client = get_client()

    async def get_me(self, user: User) -> Person:
        person = Person(**user.userinfo)
        await self.client.sync_with_dgraph(person)
        return person

    def get_people(self) -> PeopleDict:
        people = self.client.query_all()
        return people

    def search_people(self, person: Person) -> PeopleDict:
        people = self.client.search_for_person(person.name)
        return people

    def create_people(self, people: PeopleDict) -> PeopleDict:
        for person in people["people"]:
            self.client.create_person(person)
        return people

    def get_person(self, name: str) -> Person:
        db_person = self.client.search_by_name(name)
        if not db_person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'person with name {name} not found')
        return db_person

    def get_children(self, name: str) -> PeopleDict:
        children = self.client.get_children(name)
        return children

    def get_updated_children(self, name: str, children: ChildrenModel) -> PeopleDict:
        updated_children = self.client.update_children(name, children.children)
        return updated_children

    def get_parents(self, name: str) -> PeopleDict:
        parents = self.client.get_parents(name)
        return parents

    def get_partners(self, name: str) -> PeopleDict:
        partners = self.client.get_partners(name)
        return partners

    def update_partners(self, name: str, partners: PeopleDict) -> PeopleDict:
        partners = self.client.update_partners(name, partners['partners'])
        return partners

    def update_person(self, name: str, person: Person) -> Person:
        updated_person = self.client.update_person(name, person)
        return updated_person

    def delete_person(self, name: str) -> Person:
        deleted_person = self.client.delete_user(name)
        return deleted_person

    def delete_all(self):
        self.client.delete_all()
        return
