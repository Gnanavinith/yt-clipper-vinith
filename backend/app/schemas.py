from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class JobCreate(BaseModel):
    url: str

class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float

class ClipUpdate(BaseModel):
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    title: Optional[str] = None
    caption_style: Optional[str] = None
    subtitles: Optional[List[WordTimestamp]] = None

class ClipResponse(BaseModel):
    id: str
    job_id: str
    title: Optional[str]
    start_time: float
    end_time: float
    file_path: Optional[str]
    score: float
    caption_style: str
    subtitles: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: str
    url: str
    status: str
    progress: int
    failed_stage: Optional[str] = None
    error: Optional[str] = None
    clips: List[ClipResponse] = []

    class Config:
        from_attributes = True
