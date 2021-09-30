from sqlalchemy import Column, Integer, String, DateTime
from core.Initializer import db_inst
from datetime import datetime


class Videos(db_inst.Base):
    __tablename__ = "Videos"

    id = Column(String, primary_key=True, index=True)
    source = Column(String, unique=True, index=True, nullable=False)
    mp3_link = Column(String)
    download_count = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
