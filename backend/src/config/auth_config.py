import os
from dotenv import load_dotenv

def get_secret_key():
    load_dotenv()
    return os.getenv("SECRET_KEY_JWT")
