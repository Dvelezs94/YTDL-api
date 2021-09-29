"""
Database class used to conecto the DB. Do I need to explain more?
Instantiated in the 'Initializer', so if you want to use it you just need to import it like this:

from scim.core.Initializer import db_inst
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DBConnector:
    def __init__(self):
        sqlalchemy_db_url = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        self.engine = create_engine(sqlalchemy_db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()