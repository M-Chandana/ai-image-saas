import os
import json
import uuid
import redis

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from minio import Minio

from .database import engine, SessionLocal, Base
from .models import User
from .jobs import Job
from .auth import hash_password, verify_password
from .jwt import create_access_token, decode_access_token


# ================= DB =================

Base.metadata.create_all(bind=engine)


# ================= APP =================

app = FastAPI(title="AI Image SaaS")


# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)


# ================= REDIS =================

r = redis.Redis(host="ai-redis", port=6379, decode_responses=True)


# ================= MINIO =================

MINIO_BUCKET = "images"

minio = Minio(
    "ai-minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

if not minio.bucket_exists(MINIO_BUCKET):
    minio.make_bucket(MINIO_BUCKET)


# ================= DB DEP =================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= AUTH =================

security = HTTPBearer()


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = cred.credentials

    data = decode_access_token(token)

    if not data:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).filter(User.id == data["user_id"]).first()

    if not user:
        raise HTTPException(401, "User not found")

    return user


# ================= SCHEMAS =================

class Auth(BaseModel):
    email: EmailStr
    password: str


# ================= HEALTH =================

@app.get("/health")
def health():
    return {"status": "ok"}


# ================= AUTH =================

@app.post("/signup")
def signup(data: Auth, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    db.add(user)
    db.commit()

    return {"message": "Created"}


@app.post("/login")
def login(data: Auth, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(400, "Invalid credentials")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(400, "Invalid credentials")

    token = create_access_token({"user_id": user.id})

    return {"access_token": token}


# ================= UPLOAD =================

@app.post("/upload")
def upload(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Only JPG/PNG allowed")

    name = f"{user.id}/{uuid.uuid4()}_{file.filename}"

    minio.put_object(
        MINIO_BUCKET,
        name,
        file.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=file.content_type
    )

    job = Job(
        user_id=user.id,
        status="queued",
        image_path=name
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    r.rpush("jobs_queue", json.dumps({
        "job_id": job.id,
        "file": name,
        "user_id": user.id
    }))

    return {"job_id": job.id}


# ================= JOBS =================

@app.get("/jobs")
def jobs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(Job).filter(
        Job.user_id == user.id
    ).all()


# ================= FILE SERVE =================

@app.get("/files/{path:path}")
def get_file(path: str):

    try:
        data = minio.get_object(MINIO_BUCKET, path)
        return data.read()

    except:
        raise HTTPException(404, "Not found")
