from pymongo import AsyncMongoClient, MongoClient
import os
from collections import deque
from dotenv import load_dotenv

load_dotenv()

client = AsyncMongoClient(os.getenv("DB_URI"))

database = client["user_app"]

users_collection = database["users"]
research_task_collection = database["research_tasks"]

enqueue1 = deque()

sync_client = MongoClient(os.getenv("DB_URI"))