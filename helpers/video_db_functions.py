import logging
import uuid

import SQLmodels as SQLmodels
from models.video import VideoModel
from sqlalchemy import exc
from core.Initializer import db_inst

logging.basicConfig(level=logging.DEBUG)

# DB instantiation
db = db_inst.SessionLocal()
db_video = SQLmodels.Videos

# User "Pydantic" instantiation
video = VideoModel()

class VideoDBFunctions():
    
    def __init__(self):
        return

    def get_video_by_url(self, video_url: str):
        return db.query(db_video).filter(db_video.source == video_url).first()

    def get_videos(self, skip: int = 0, limit: int = 100):
        return db.query(db_video).offset(skip).limit(limit).all()

    def create_video(self, video_url: str):
        downloaded_video = video.download_as_mp3(video_url = video_url)
        logging.info(downloaded_video)
        return "Video Downloaded!"