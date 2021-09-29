from sqlalchemy import Column, Integer, String, DateTime
from core.Initializer import db_inst


class Videos(db_inst.Base):
    __tablename__ = "Videos"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, nullable=False)
    mp3_link = Column(String)
    created_at = Column(DateTime, nullable=False)
    downloaded_times = Column(Integer, nullable=False)