from typing import Optional
from helpers.video_db_functions import VideoDBFunctions
from core.Initializer import db_inst
import SQLmodels as SQLmodels
from fastapi import FastAPI

app = FastAPI()
video_db = VideoDBFunctions()

# Run "migrations"
SQLmodels.db_inst.Base.metadata.create_all(bind=db_inst.engine)

@app.get("/")
def read_root():
    video_db.get_video_by_url(video_url="google.com")
    return {"data": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
