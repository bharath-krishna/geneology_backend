import json

import pydgraph
from fastapi.exceptions import HTTPException
from starlette import status

from configs.logging import logger
from models.person import Person


class DgraphClient():
    def __init__(self):
        self.client_stub = pydgraph.DgraphClientStub('localhost:9080')
        self.client = pydgraph.DgraphClient(self.client_stub)

    def drop_all(self):
        return self.client.alter(pydgraph.Operation(drop_all=True))

    async def sync_with_dgraph(self, person: Person):
        person.created_by = person.email
        await person.normalize()
        self.create_user(person)
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
        return self.client.alter(pydgraph.Operation(schema=schema))

    def create_user(self, person: Person):
        txn = self.client.txn()
        query = """{
            person as var(func: eq(email, "%s"))
        }""" % person.email

        person_obj = {k: v for k, v in person.dict().items() if v}
        person_obj['uid'] = 'uid(person)'
        mutation = txn.create_mutation(set_obj=person_obj)
        request = txn.create_request(query=query, mutations=[mutation], commit_now=True)
        txn.do_request(request)
        return self.search_by_email(person.email)

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
                logger.info(f"{person['name']} deleted from db")
            txn.commit()
        finally:
            txn.discard()

    def delete_user(self, email):
        txn = self.client.txn()
        try:
            query1 = """query all($a: string) {
                all(func: eq(email, $a)) {
                uid
                }
            }"""
            variables1 = {'$a': email}
            res1 = self.client.txn(read_only=True).query(query1, variables=variables1)
            ppl1 = json.loads(res1.json)
            for person in ppl1['all']:
                logger.info(f"Bob  UID: {person['uid']}")
                txn.mutate(del_obj=person)
                logger.info(f"{person['name']} deleted")
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
                parents {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                }
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
            logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
        elif not len(response['person']):
            error_message = f'no matches found for {email}'
            logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
        return response['person'][0]

    def query_all(self):
        query = """{
            people(func: has(name)) {
                name
                email
                gender
                kcid
                parents
                partners
                children
                created_by
                username
            }
        }"""
        res = self.client.txn(read_only=True).query(query)
        ppl = json.loads(res.json)
        return ppl

    def update_person(self, email: str, update_person: Person):
        txn = self.client.txn()
        person = self.search_by_email(email)
        if person:
            update_person.uid = person['uid']
        obj = update_person.dict()
        mutation = txn.create_mutation(set_obj=obj)
        request = txn.create_request(mutations=[mutation], commit_now=True)
        txn.do_request(request)
        txn.discard()
        return update_person

    def get_children(self, email):
        query = """
        {
            person(func: eq(email, "%s")) {
                children {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    parents
                    partners
                    children
                }
                ~children {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    parents
                    partners
                    children
                }
            }
        }
        """ % email
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if not len(response['person']):
            return []
        # Remove ~ from ~children key
        if '~children' in response['person'][0]:
            if 'children' not in response['person'][0]:
                response['person'][0]['children'] = []
            response['person'][0]['children'].extend(response['person'][0].pop('~children'))
        return response['person'][0]

    def get_parents(self, email):
        query = """
        {
            person(func: eq(email, "%s")) {
                parents {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    parents
                    partners
                    children
                }
                ~parents {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    parents
                    partners
                    children
                }
            }
        }
        """ % email
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if len(response['person']) > 2:
            error_message = f'found more than 2 parents for email {email}'
            logger.warning(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
        elif not len(response['person']):
            return []
        # Remove ~ from ~partners key
        if '~parents' in response['person'][0]:
            if 'parents' not in response['person'][0]:
                response['person'][0]['parents'] = []
            response['person'][0]['parents'].extend(response['person'][0].pop('~parents'))
        return response['person'][0]

    def get_partners(self, email):
        query = """
        {
            person(func: eq(email, "%s")) {
                partners {
                    uid
                    name
                    kcid
                    gender
                    email
                    created_by
                    username
                    parents
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
                    parents
                    partners
                    children
                }
            }
        }
        """ % email
        res = self.client.txn(read_only=False).query(query)
        response = json.loads(res.json)
        if not len(response['person']):
            return []
        # Remove ~ from ~partners key
        if '~partners' in response['person'][0]:
            if 'partners' not in response['person'][0]:
                response['person'][0]['partners'] = []
            response['person'][0]['partners'].extend(response['person'][0].pop('~partners'))
        return response['person'][0]
