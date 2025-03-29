import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRETKEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///quizdb.sqlite3"
    DEBUG = True