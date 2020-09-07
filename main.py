import uvicorn
from config import PORT, LOG_LEVEL, RELOAD, WORKERS


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(PORT), log_level=LOG_LEVEL, reload=RELOAD,
        workers=WORKERS, access_log=True
    )
