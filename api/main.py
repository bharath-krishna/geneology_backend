import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.client import get_api_client
from api.configurations.base import config
from api.routers import people, users


class Application(FastAPI):
    def __init__(self, **kwargs):
        self.client = get_api_client()
        config.logger.info("Application starting")
        super().__init__(on_startup=[self.client.on_startup], on_shutdown=[self.client.on_shutdown], **kwargs)


app = Application(docs_url='/',
                  swagger_ui_oauth2_redirect_url='/callback',
                  title=config.title,
                  description="Backend apis for building family tree used in geneology project",
                  version="1.0.0")

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(people.router, prefix=config.prefix)
app.include_router(users.router, prefix=config.prefix)
