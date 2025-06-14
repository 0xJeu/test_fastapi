import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from db.core import DatabaseManager

router = APIRouter(prefix="/users", tags=["users"])


db = DatabaseManager.from_env()


class User(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8)


@router.get("/")
def list_users():
    users = db.users.get_all_users()
    logging.info(f"Users Size: {len(users)}")
    for user in users:
        logging.info(f"User: {user}")
    return {"users": users}


@router.get("/{user_id}")
def get_user(user_id: int):
    logging.info(f"Getting user by ID: {user_id}")
    user = db.users.get_user_by_id(user_id)
    return {"user": user}


@router.post("/")
def create_user(user: User):
    logging.info(f"Creating user: {user.name}, {user.email}")
    db.users.create_user(user.name, user.email, user.password)
    return {"message": "User created"}


@router.put("/{user_id}")
def update_user(user_id: int, user: User):
    logging.info(f"Updating user: {user_id}, {user.name}, {user.email}")
    data = {"name": user.name, "email": user.email, "password": user.password}
    db.users.update_user(user_id, data)
    return {"message": "User updated"}
