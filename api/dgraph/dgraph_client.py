import json
from functools import lru_cache
from typing import List

import pydgraph
from api.configurations.base import config
from api.models.person import Person
from fastapi.exceptions import HTTPException
from starlette import status


@lru_cache()
def get_client():
    return DgraphClient()


class DgraphClient():
    def __init__(self):
        self.client_stub = pydgraph.DgraphClientStub(f"{config.db_host}:{config.db_port}")
        self.client = pydgraph.DgraphClient(self.client_stub)

    def drop_all(self):
        return self.client.alter(pydgraph.Operation(drop_all=True))

    async def sync_with_dgraph(self, person: Person):
        person.created_by = person.email
        await person.normalize()
        self.create_person(person)
        return

    def close_client_stub(self):
        # Close the client stub.
        self.client_stub.close()

    # Set schema.
    def set_schema(self):
        schema = """
            type Person {
                sub
                name
                email
                kcid
                gender
                created_by
                username
                partners
                children
            }
            sub: string .
            name: string @index(term) .
            email: string @index(term) .
            kcid: string .
            gender: string .
            created_by: string .
            username: string @index(term) .
            partners: [uid] @reverse .
            children: [uid] @reverse .
        """
        try:
            return self.client.alter(pydgraph.Operation(schema=schema))
        except Exception:
            raise Exception('Failed to start server. Could not connect to dgraph hosts')

    def create_person(self, person: Person):
        txn = self.client.txn()
        query = """{
            person as var(func: eq(name, "%s"))
        }""" % person.name

        person_obj = {k: v for k, v in person.dict().items() if v}
        person_obj['uid'] = 'uid(person)'
        mutation = txn.create_mutation(set_obj=person_obj)
        request = txn.create_request(query=query, mutations=[mutation], commit_now=True)
        txn.do_request(request)
        return self.search_by_name(person.name)

    def delete_all(self):
        txn = self.client.txn()
        try:
            query1 = """{
                all(func: has(name)) {
                    uid
                    name
                    email
                    gender
                }
            }"""
            res1 = self.client.txn(read_only=True).query(query1)
            ppl1 = json.loads(res1.json)
            for person in ppl1['all']:
                txn.mutate(del_obj=person)
                config.logger.info(f"{person['name']} deleted from db")
            txn.commit()
        finally:
            txn.discard()

    def delete_user(self, name: str):
        txn = self.client.txn()
        try:
            query1 = """query all($a: string) {
                people(func: eq(name, $a)) {
                    uid
                    name
                }
            }"""
            variables1 = {'$a': name}
            res1 = self.client.txn(read_only=True).query(query1, variables=variables1)
            people = json.loads(res1.json)
            if not people['people']:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f'Not found. No person with name {name} found in database')
            for person in people['people']:
                txn.mutate(del_obj=person)
                config.logger.info(f"{person} deleted")
            txn.commit()
        finally:
            txn.discard()

    def search_by_email(self, email) -> Person:
        query = """
        {
            person(func: eq(email, "%s")) {
                uid
                name
                kcid
                gender
                email
                created_by
                username
                partners {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                }
                children {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                }
            }
        }
        """ % email
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if len(response['person']) > 1:
            error_message = f'found multiple results for email {email}'
            config.logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
        elif not len(response['person']):
            error_message = f'no matches found for {email}'
            config.logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        return response['person'][0]

    def search_by_name(self, name) -> Person:
        query = """
        {
            person(func: eq(name, "%s")) {
                uid
                name
                kcid
                gender
                email
                created_by
                username
                partners {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                }
                children {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                }
            }
        }
        """ % name
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if len(response['person']) > 1:
            error_message = f'found multiple results for name {name}'
            config.logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
        elif not len(response['person']):
            error_message = f'no matches found for {name}'
            config.logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        return response['person'][0]

    def search_for_person(self, name) -> Person:
        query = """
        {
            person(func: eq(name, "%s")) {
                uid
                name
                kcid
                gender
                email
                created_by
                username
                partners {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                }
                children {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                }
            }
        }
        """ % name
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        return response['person']

    def query_all(self):
        query = """{
            people(func: has(name)) {
                uid
                sub
                name
                email
                gender
                partners
                children
                created_by
                username
            }
        }"""
        res = self.client.txn(read_only=True).query(query)
        ppl = json.loads(res.json)
        return ppl

    def update_person(self, name: str, update_person: Person):
        txn = self.client.txn()
        person = self.search_by_name(name)
        if person:
            update_person.uid = person['uid']
        obj = update_person.dict()
        mutation = txn.create_mutation(set_obj=obj)
        request = txn.create_request(mutations=[mutation], commit_now=True)
        txn.do_request(request)
        txn.discard()
        return update_person

    def get_children(self, name):
        query = """
        {
            person(func: eq(name, "%s")) {
                children {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    partners
                    children
                }
            }
        }
        """ % name
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if not len(response['person']):
            return {"children": []}
        return response['person'][0]

    def update_children(self, name: str, children: List[Person]):
        txn = self.client.txn()
        # query = """{
        #     person as var(func: eq(name, "%s"))
        # }""" % name

        person = self.search_by_name(name)

        # person['uid'] = 'uid(person)'
        if not person.get('children'):
            person['children'] = []
        else:
            for child in children:
                if child.name in [c['name'] for c in person['children']]:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                        detail=f'person with name {child.name} already exist as children for {name}')
        for child in children:
            person['children'].append(child.dict())

        mutation = txn.create_mutation(set_obj=person)
        request = txn.create_request(mutations=[mutation], commit_now=True)
        txn.do_request(request)
        return self.get_children(person['name'])

    def get_parents(self, name):
        query = """
        {
            person(func: eq(name, "%s")) {
                parents: ~children {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    partners
                    children
                }
            }
        }
        """ % name
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if len(response['person']) > 2:
            error_message = f'found more than 2 parents for email {name}'
            config.logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
        elif not len(response['person']):
            return {"parents": []}
        return response['person'][0]

    def get_partners(self, name):
        query = """
        {
            person(func: eq(name, "%s")) {
                partners {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    partners
                    children
                }
                ~partners {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    partners
                    children
                }
            }
        }
        """ % name
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if not len(response['person']):
            return {"partners": []}
        # Remove ~ from ~partners key
        if '~partners' in response['person'][0]:
            if 'partners' not in response['person'][0]:
                response['person'][0]['partners'] = []
            response['person'][0]['partners'].extend(response['person'][0].pop('~partners'))
        return response['person'][0]

    def update_partners(self, name: str, partners: List[Person]):
        txn = self.client.txn()
        person = self.search_by_name(name)

        if not person.get('partners'):
            person['partners'] = []
        else:
            for partner in partners:
                if partner.name in [p['name'] for p in person['partners']]:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                        detail=f'person with name {partner.name} already exist as partner for {name}')
        for partner in partners:
            person['partners'].append(partner.dict())

        mutation = txn.create_mutation(set_obj=person)
        request = txn.create_request(mutations=[mutation], commit_now=True)
        txn.do_request(request)
        return self.get_partners(name)
