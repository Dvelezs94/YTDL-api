"""
All the functions that run before database initialization should go here

Order:
 1. Sets environment variables
 2. Init DB connection
"""

import os
from database import DBConnector

# instantiating the database at this point because secrets need to load first
db_inst = DBConnector()