import datetime
import json
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import (OAuth2, OAuth2AuthorizationCodeBearer,
                              OAuth2PasswordBearer, OAuth2PasswordRequestForm)
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2, OAuthFlows, OAuthFlowImplicit
from pydantic import BaseModel

import pydgraph
from api import app
from api.models.person import Person


# Create a client stub.
def create_client_stub():
    return pydgraph.DgraphClientStub('localhost:9080')


# Create a client.
def create_client(client_stub):
    return pydgraph.DgraphClient(client_stub)


# Drop All - discard all data and start from a clean slate.
def drop_all(client):
    return client.alter(pydgraph.Operation(drop_all=True))


# Set schema.
def set_schema(client):
    schema = """
    name: string @index(exact) .
    friend: [uid] @reverse .
    age: int .
    married: bool .
    loc: geo .
    dob: datetime .
    type Person {
        name
        friend
        age
        married
        loc
        dob
    }
    """
    return client.alter(pydgraph.Operation(schema=schema))


# Create data using JSON.
def create_data(client):
    # Create a new transaction.
    txn = client.txn()
    try:
        # Create data.
        p = {
            'uid': '_:alice',
            'dgraph.type': 'Person',
            'name': 'Alice',
            'age': 26,
            'married': True,
            'loc': {
                'type': 'Point',
                'coordinates': [1.1, 2],
            },
            'dob': datetime.datetime(1980, 1, 1, 23, 0, 0, 0).isoformat(),
            'friend': [
                {
                    'uid': '_:bob',
                    'dgraph.type': 'Person',
                    'name': 'Bob',
                    'age': 24,
                }
            ],
            'school': [
                {
                    'name': 'Crown Public School',
                }
            ]
        }

        # Run mutation.
        response = txn.mutate(set_obj=p)

        # Commit transaction.
        txn.commit()

        # Get uid of the outermost object (person named "Alice").
        # response.uids returns a map from blank node names to uids.
        print('Created person named "Alice" with uid = {}'.format(response.uids['alice']))

    finally:
        # Clean up. Calling this after txn.commit() is a no-op and hence safe.
        txn.discard()


# Deleting a data
def delete_data(client):
    # Create a new transaction.
    txn = client.txn()
    try:
        query1 = """query all($a: string) {
            all(func: eq(name, $a)) {
               uid
            }
        }"""
        variables1 = {'$a': 'Bob'}
        res1 = client.txn(read_only=True).query(query1, variables=variables1)
        ppl1 = json.loads(res1.json)
        for person in ppl1['all']:
            print("Bob's UID: " + person['uid'])
            txn.mutate(del_obj=person)
            print('Bob deleted')
        txn.commit()

    finally:
        txn.discard()


# Query for data.
def query_alice(client):
    # Run query.
    query = """query all($a: string) {
        all(func: eq(name, $a)) {
            uid
            name
            age
            married
            loc
            dob
            friend {
                name
                age
            }
            school {
                name
            }
        }
    }"""

    variables = {'$a': 'Alice'}
    res = client.txn(read_only=True).query(query, variables=variables)
    ppl = json.loads(res.json)

    # Print results.
    print('Number of people named "Alice": {}'.format(len(ppl['all'])))


# Query to check for deleted node
def query_bob(client):
    query = """query all($b: string) {
            all(func: eq(name, $b)) {
                uid
                name
                age
                friend {
                    uid
                    name
                    age
                }
                ~friend {
                    uid
                    name
                    age
                }
            }
        }"""

    variables = {'$b': 'Bob'}
    res = client.txn(read_only=True).query(query, variables=variables)
    ppl = json.loads(res.json)

    # Print results.
    print('Number of people named "Bob": {}'.format(len(ppl['all'])))

# Query to check for deleted node
def query_all(client):
    query = """{
        persons(func: has(name)) {
            uid
            expand(_all_) {
            uid
            name
            }
        }
    }"""
    # variables = {'$b': 'Bob'}
    # res = client.txn(read_only=True).query(query, variables=variables)
    res = client.txn(read_only=True).query(query)
    ppl = json.loads(res.json)

    # Print results.
    return ppl



# items = {"foo": "The Foo Wrestlers"}

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# # @app.get("/items/{item_id}")
# # async def read_item(item_id: str):
# #     if item_id not in items:
# #         raise HTTPException(status_code=404, detail="Item not found")
# #     return {"item": items[item_id]}

# # @app.post("/people", response_model=Dict[str, List[Person]])
# # async def update_people(person: Person):
# #     client_stub = create_client_stub()
# #     client = create_client(client_stub)
# #     # drop_all(client)
# #     # set_schema(client)
# #     # create_data(client)
# #     # query_alice(client)  # query for Alice
# #     # query_bob(client)  # query for Bob
# #     # delete_data(client)  # delete Bob
# #     # query_alice(client)  # query for Alice
# #     # query_bob(client)  # query for Bob

# #     dd = query_all(client)
# #     # Close the client stub.
# #     client_stub.close()
# #     return dd






fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8099/auth/realms/demo/protocol/openid-connect/token")
# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     authorizationUrl='http://localhost:8099/auth/realms/demo/protocol/openid-connect/auth',
#     tokenUrl='http://localhost:8099/auth/realms/demo/protocol/openid-connect/token',
# )


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    import ipdb; ipdb.set_trace()
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# @app.post("/tokens")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")

#     return {"access_token": user.username, "token_type": "bearer"}


# @app.get("/users/me")
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user
