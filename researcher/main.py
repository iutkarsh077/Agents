from agent import process_research_tasks
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pymongo import  AsyncMongoClient
import os
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import asyncio
from db import research_task_collection, users_collection, enqueue1

load_dotenv()

app = FastAPI()


class UserSchema(BaseModel):
    name: str
    email: str
    password: str


class ResearchTaskSchema(BaseModel):
    user_id: str
    task: str

client = AsyncMongoClient(os.getenv("DB_URI"))


@app.post("/save-user")
async def save_user(user: UserSchema):
    try:
        user_data = user.model_dump()
        findUser = await users_collection.find_one({ "email": user_data["email"] })
    
        if findUser:
            raise HTTPException(status_code=400, detail="User already exists")
        
        await users_collection.insert_one({"email": user_data["email"], "name": user_data["name"], "password": user_data["password"] })
        return {"message": "User saved successfully"}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={'error': str(e)})


@app.post("/research-task")
async def research_task(task: ResearchTaskSchema):
    try:
        task_data = task.model_dump()

        data = await research_task_collection.insert_one({ "user_id": ObjectId(task_data["user_id"]), "task": task_data["task"], "status": "pending", "research_data": [] })

        task_data["_id"] = data.inserted_id
        enqueue1.append(task_data)
        print(enqueue1)

        asyncio.create_task(process_research_tasks())

        return JSONResponse(status_code=200, content={'message': 'Task enqueued successfully'})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={'error': str(e)})
        