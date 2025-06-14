import logging
from typing import Dict, List, Optional


class PostCRUD:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_posts(self) -> List[Dict]:
        """Get all posts from the database"""
        query = "SELECT * FROM posts"
        logging.info("Getting all posts")
        return self.db_manager.fetch_all(query)

    def get_post_by_id(self, post_id: int) -> Optional[Dict]:
        """Get a post by its ID"""
        query = "SELECT * FROM posts WHERE id = %s"
        logging.info(f"Getting post by ID: {post_id}")
        return self.db_manager.fetch_one(query, (post_id,))

    def get_posts_by_user_id(self, user_id: int) -> List[Dict]:
        """Get all posts by a user's ID"""
        query = "SELECT * FROM posts WHERE user_id = %s"
        logging.info(f"Getting posts by user ID: {user_id}")
        return self.db_manager.fetch_all(query, (user_id,))

    def create_post(self, title: str, content: str, user_id: int) -> bool:
        """Create a new post in the database"""
        query = "INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)"
        logging.info(f"Creating post: {title}, {content}, {user_id}")
        return self.db_manager.execute_query(query, (title, content, user_id))
