from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    status = Column(String, default="queued")

    image_path = Column(String)
    overlay_path = Column(String)
    csv_path = Column(String)

    model_name = Column(String, default="yolov8n")
    model_version = Column(String, default="8.0")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
