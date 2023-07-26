from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
    REDIS_PASS = os.getenv("REDIS_PASS")
    REDIS_HOST = os.getenv("REDIS_HOST")
    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")


settings = Settings()
