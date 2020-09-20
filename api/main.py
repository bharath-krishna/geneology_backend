import uvicorn
from fastapi import FastAPI

from client import AiohttpClient
from configs import LOG_LEVEL, PORT, RELOAD, WORKERS
from configs.logging import logger
from dgraph.dgraph_client import DgraphClient
from routers import people, users


class Application(FastAPI):
    def __init__(self, **kwargs):
        self.client = AiohttpClient()
        self.dg = DgraphClient()
        self.dg.set_schema()
        logger.info("Application starting")
        super().__init__(on_startup=[self.client.on_startup], on_shutdown=[self.client.on_shutdown], **kwargs)


app = Application(docs_url='/', swagger_ui_oauth2_redirect_url='/callback')
app.include_router(users.router)
app.include_router(people.router)

if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    # log_config["formatters"]["access"]["fmt"] = '%(asctime)s %(levelname)s - %(message)s'
    log_config["formatters"]["access"]["fmt"] = ('{"time": \"%(asctime)s\", "level": \"%(levelname)s\", '
                                                 '"name": \"[%(name)s]\", "message": \"%(message)s\"}')
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=int(PORT),
                log_level=LOG_LEVEL,
                reload=RELOAD,
                workers=WORKERS,
                access_log=True,
                log_config=log_config,
                debug=True)
