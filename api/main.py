from fastapi import FastAPI

from api.client import AiohttpClient
from api.configs.logging import logger
from api.dgraph.dgraph_client import DgraphClient
from api.routers import people, users


class Application(FastAPI):
    def __init__(self, **kwargs):
        self.client = AiohttpClient()
        self.dg = DgraphClient()
        self.dg.set_schema()
        logger.info("Application starting")
        super().__init__(on_startup=[self.client.on_startup], on_shutdown=[self.client.on_shutdown], **kwargs)


app = Application(
    docs_url='/',
    swagger_ui_oauth2_redirect_url='/callback',
    title="Geneology Project - Backend",
    description="Backend apis for building family tree used in geneology project",
    version="1.0.0",
)
app.include_router(people.router)
app.include_router(users.router)
