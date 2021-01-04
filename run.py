import uvicorn

from api.configurations.base import config

if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    # log_config["formatters"]["access"]["fmt"] = '%(asctime)s %(levelname)s - %(message)s'
    log_config["formatters"]["access"]["fmt"] = ('{"time": \"%(asctime)s\", "level": \"%(levelname)s\", '
                                                 '"name": \"[%(name)s]\", "message": \"%(message)s\"}')
    uvicorn.run("api.main:app",
                host=config.host,
                port=config.port,
                log_level=config.log_level,
                reload=config.reload,
                workers=config.workers,
                access_log=config.access_log,
                log_config=log_config,
                debug=config.debug)
