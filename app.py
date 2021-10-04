import os
from typing import Any, Dict
from controllers.video import Video
from core.Initializer import db_inst
import SQLmodels as SQLmodels
from fastapi import FastAPI, status
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import logging

# CORS config
middleware = [ Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])]


app = FastAPI(title="YTDL", middleware=middleware)

video_db = Video()

logging.basicConfig(level=logging.DEBUG)
# Run "migrations"
SQLmodels.db_inst.Base.metadata.create_all(bind=db_inst.engine)

@app.get("/")
def read_root():
    return {"data": "I'm working"}


@app.post("/video", status_code=status.HTTP_201_CREATED)
async def process_video(request: Dict[Any, Any]): # body param
    resp = video_db.create_video(video_url = request["video_src"])
    return resp

# handler = Mangum(app)
