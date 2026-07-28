import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "finz_challenge"
)

client = AsyncIOMotorClient(MONGODB_URI)
database = client[DATABASE_NAME]


def get_database():
    return database