from dotenv import load_dotenv
import os

load_dotenv()

DB_DRIVER = str(os.getenv('DB_DRIVER'))
DB_NAME = str(os.getenv('DB_NAME'))
DB_USER = str(os.getenv('DB_USER'))
DB_PASS = str(os.getenv('DB_PASS'))
DB_HOST = str(os.getenv('DB_HOST'))
DB_PORT = str(os.getenv('DB_PORT'))

REDIS_HOST = str(os.getenv('REDIS_HOST'))
REDIS_PORT = str(os.getenv('REDIS_PORT'))
REDIS_PASSWORD = str(os.getenv('REDIS_PASSWORD'))

NOVA_POST_API = str(os.getenv('NOVA_POST_API'))

ADMIN_USERNAME = str(os.getenv('ADMIN_USERNAME'))
ADMIN_PASSWORD = str(os.getenv('ADMIN_PASSWORD'))
SESSION_TOKEN_LENGTH = str(os.getenv('SESSION_TOKEN_LENGTH'))
