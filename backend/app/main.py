from fastapi import FastAPI, Depends
from .auth import auth_backend, current_active_user, fastapi_users
from .schemas import UserRead, UserCreate
from .models import User
from .database import engine, Base
from .routers import uploads
from .storage import storage_service

app = FastAPI(
    title="Quizmarize API",
    description="An API to summarize content and generate quizzes.",
    version="0.1.0"
)

# Include the routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"]
)
app.include_router(uploads.router, prefix="/content") # <-- Add the uploads router

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Welcome to the Quizmarize API!"}


@app.get("/protected-route", tags=["Users"], response_model=UserRead)
def get_current_user_data(user: User = Depends(current_active_user)):
    return user

@app.on_event("startup")
async def on_startup():
    storage_service.ensure_bucket_exists()
    async with engine.begin() as conn:
        # This will create all tables, including FastAPI Users' tables
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully!")
