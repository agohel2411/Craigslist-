from fastapi import FastAPI
from src.log import logger
from router import sqlrouter, jsonrouter
import uvicorn

app = FastAPI()

logger.info(f"API Loaded")

app.include_router(sqlrouter.router)
app.include_router(jsonrouter.router)

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port='10001')