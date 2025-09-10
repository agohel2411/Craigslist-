from fastapi import FastAPI
from src.log import logger
from router import sqlrouter, jsonrouter

app = FastAPI()

logger.info(f"API Loaded")

app.include_router(sqlrouter.router)
app.include_router(jsonrouter.router)