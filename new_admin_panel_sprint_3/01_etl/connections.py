import os
from dotenv import load_dotenv


load_dotenv()

DSL = {
    "dbname": os.environ.get('DB_NAME'),
    "user": os.environ.get('DB_USER'),
    "password": os.environ.get('DB_PASSWORD'),
    "host": os.environ.get('DB_HOST'),
    "port": os.environ.get('DB_PORT'),
}

JSON_STORE = os.environ.get('JSON_STORE')

URL = f"http://{os.environ.get('ES_HOST')}:{os.environ.get('ES_PORT')}"
