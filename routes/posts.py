import logging
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from db.core import DatabaseManager

router = APIRouter(prefix="/posts", tags=["posts"])

db = DatabaseManager.from_env()


class Post(BaseModel):
    post_id: int = Field(gt=0)
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=3, max_length=255)
    user_id: int = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")


@router.get("/")
def list_posts():
    posts = db.posts.get_all_posts()
    logging.info(f"Posts Size: {len(posts)}")
    for post in posts:
        logging.info(f"Post: {post}")
    return {"posts": posts}


@router.get("/{post_id}")
def get_post(post_id: int):
    post = db.posts.get_post_by_id(post_id)
    logging.info(f"Getting post by ID: {post_id}")
    return {"post": post}


@router.post("/")
def create_post(post: Post):
    logging.info(f"Creating post: {post.title}, {post.content}, {post.user_id}")
    db.posts.create_post(post.title, post.content, post.user_id)
    return {"message": "Post created"}


@router.put("/{post_id}")
def update_post(post_id: int, post: Post):
    logging.info(
        f"Updating post: {post_id}, {post.title}, {post.content}, {post.user_id}"
    )
    db.posts.update_post(post_id, post.title, post.content, post.user_id)
    return {"message": "Post updated"}


@router.delete("/{post_id}")
def delete_post(post_id: int):
    logging.info(f"Deleting post: {post_id}")
    db.posts.delete_post(post_id)
    return {"message": "Post deleted"}


@router.get("/user/{user_id}")
def get_posts_by_user(user_id: int):
    logging.info(f"Getting posts by user ID: {user_id}")
    posts = db.posts.get_posts_by_user_id(user_id)
    return {"posts": posts}
