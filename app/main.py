from fastapi import FastAPI
from core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# include your API routers here later
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix=settings.API_V1_STR)