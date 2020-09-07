import time
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

from api.handlers import simple
from api import middlewares