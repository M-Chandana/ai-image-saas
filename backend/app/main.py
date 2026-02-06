import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from .jwt import create_access_token
from .database import engine, SessionLocal
from .database import Base
from .models import User
from .jobs import Job
from .auth import hash_password, verify_password
from fastapi import FastAPI
from fastapi.security import HTTPBearer
from . import models, jobs
from fastapi.openapi.utils import get_openapi

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

security = HTTPBearer()

app = FastAPI(
    title="AI Image SaaS",
    version="0.1.0",
    openapi_tags=[
        {"name": "Auth", "description": "Authentication routes"},
        {"name": "Images", "description": "Image processing routes"},
    ],
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True
    }
)

app.openapi_schema = None



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Image SaaS",
        version="0.1.0",
        description="AI Image Processing SaaS",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [
        {
            "BearerAuth": []
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class JobResponse(BaseModel):
    id: int
    status: str


# Health
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


# Signup
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    exists = db.query(User).filter(User.email == user.email).first()

    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)

    new_user = User(
    email=user.email,
    hashed_password=hashed
)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


# Login
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(
        data={"user_id": db_user.id, "email": db_user.email}
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }



# Upload Image (Create Job)
@app.post("/upload/{user_id}")
def upload_image(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPG and PNG allowed")

    filename = f"{user_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job = Job(
        user_id=user_id,
        status="queued",
        image_path=file_path
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "status": job.status
    }


# List Jobs
@app.get("/jobs/{user_id}")
def list_jobs(user_id: int, db: Session = Depends(get_db)):

    jobs = db.query(Job).filter(Job.user_id == user_id).all()

    return jobs
