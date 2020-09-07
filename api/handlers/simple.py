from fastapi import FastAPI
from api.models.person import Person
from api import app

items = {"foo": "The Foo Wrestlers"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}

@app.post("/people", response_model=Person)
async def update_people(person: Person):
    return person
