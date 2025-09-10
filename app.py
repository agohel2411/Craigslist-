from fastapi import FastAPI
from src import model
from src.database import engine
from src.log import logger
from router import sqlrouter, jsonrouter


model.Base.metadata.create_all(bind=engine)

app = FastAPI()

logger.info(f"API Loaded")

app.include_router(sqlrouter.router)
app.include_router(jsonrouter.router)
