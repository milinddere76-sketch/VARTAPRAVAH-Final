from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NewsArticle(BaseModel):
    title: str
    content: str
    source: str
    published_at: Optional[datetime] = None

class VideoStats(BaseModel):
    video_id: str
    status: str
    duration: float
    created_at: datetime

class AnalyticsData(BaseModel):
    total_videos: int
    total_errors: int
    estimated_revenue: float
    timestamp: datetime
