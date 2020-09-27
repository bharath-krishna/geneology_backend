import uvicorn

from api.configs import LOG_LEVEL, PORT, RELOAD, WORKERS

if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    # log_config["formatters"]["access"]["fmt"] = '%(asctime)s %(levelname)s - %(message)s'
    log_config["formatters"]["access"]["fmt"] = ('{"time": \"%(asctime)s\", "level": \"%(levelname)s\", '
                                                 '"name": \"[%(name)s]\", "message": \"%(message)s\"}')
    uvicorn.run("api.main:app",
                host="0.0.0.0",
                port=int(PORT),
                log_level=LOG_LEVEL,
                reload=RELOAD,
                workers=WORKERS,
                access_log=True,
                log_config=log_config,
                debug=True)
