from typing import Any, Dict
from helpers.video_db_functions import VideoDBFunctions
from core.Initializer import db_inst
import SQLmodels as SQLmodels
from fastapi import FastAPI, Request
import logging

app = FastAPI()
video_db = VideoDBFunctions()

logging.basicConfig(level=logging.DEBUG)
# Run "migrations"
SQLmodels.db_inst.Base.metadata.create_all(bind=db_inst.engine)

@app.get("/")
def read_root():
    return {"data": "Hello World"}


@app.post("/new_video/")
async def process_video(request: Dict[Any, Any]): # body param
    video_db.create_video(video_url = request["video_src"])
    return {"data": "video processing"}
