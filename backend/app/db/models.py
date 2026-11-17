from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, downloading, transcribing, analyzing, cutting, reframing, subtitling, completed, failed
    progress = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    clips = relationship("ClipModel", back_populates="job", cascade="all, delete-orphan")

class ClipModel(Base):
    __tablename__ = "clips"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    title = Column(String, nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    file_path = Column(String, nullable=True)
    score = Column(Float, default=0.0)
    subtitles_json = Column(Text, nullable=True) # JSON string storing words with start/end
    caption_style = Column(String, default="default")

    job = relationship("Job", back_populates="clips")
