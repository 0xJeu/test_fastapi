import logging

from dotenv import load_dotenv  # Import load_dotenv
from fastapi import FastAPI

from db import DatabaseManager

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Initialize DatabaseManager from environment variables
db = DatabaseManager.from_env()

app = FastAPI()


@app.get("/")
def list_users():
    users = db.users.get_all_users()
    logging.info(f"Users Size: {len(users)}")
    for user in users:
        logging.info(f"User: {user}")
    return {"users": users}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.users.get_user_by_id(user_id)
    return {"user": user}


@app.post("/users")
def create_user(name: str, email: str, password: str):
    db.users.create_user(name, email, password)
    return {"message": "User created"}


@app.put("/users/{user_id}")
def update_user(user_id: int, name: str, email: str, password: str):
    db.users.update_user(user_id, name, email, password)
    return {"message": "User updated"}
