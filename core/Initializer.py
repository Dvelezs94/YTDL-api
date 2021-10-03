"""
All the functions that run before database initialization should go here

Order:
 1. Sets environment variables
 2. Init DB connection
"""

import os
from database import DBConnector
from common.SecretsManager import SecretsManager
from dotenv import load_dotenv
import logging


logging.basicConfig(level=logging.DEBUG)

# load .secrets file if it exists and load them into env vars on local env
if os.path.exists(".secrets") and os.getenv('LOCAL_ENV') == "true":
    load_dotenv(".secrets")

# If is not local environment, then fetch secrets from SSM and export them as env variables
# if os.getenv('LOCAL_ENV') != "true":
#     secrets_name_base = os.getenv('SECRETS_NAME_BASE')
#     aws_region = os.getenv('AWS_REGION', 'us-east-1')
#     logging.info("=== Secrets start pull")
#     secrets_manager = SecretsManager(secrets_name_base, aws_region)
#     secrets = secrets_manager.get_all_path_secrets()
#     logging.info("=== Fetched secrets")
#     # iterate through all secrets and export them as env vars     
#     for secret in secrets:
#         os.environ[secret] = secrets[secret]

logging.info("Starting Db connection...")
# instantiating the database at this point because secrets need to load first
db_inst = DBConnector()
logging.info("DB is now connected")