import logging
from typing import Any, Dict, List, Optional


class UserCRUD:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_user(self, name: str, email: str, password: str) -> bool:
        """Create a new user in the database"""
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        logging.info(f"Creating user: {name}, {email}, {password}")
        return self.db_manager.execute_query(query, (name, email, password))

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get a user by their ID"""
        query = "SELECT * FROM users WHERE id = %s"
        logging.info(f"Getting user by ID: {user_id}")
        return self.db_manager.fetch_one(query, (user_id,))

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get a user by their email"""
        query = "SELECT * FROM users WHERE email = %s"
        logging.info(f"Getting user by email: {email}")
        return self.db_manager.fetch_one(query, (email,))

    def get_all_users(self) -> List[Dict]:
        """Get all users from the database"""
        query = "SELECT * FROM users"
        logging.info("Getting all users")
        return self.db_manager.fetch_all(query)

    def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Update a user's information"""
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())
        values.append(user_id)

        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        logging.info(f"Updating user: {user_id}, {data}")
        return self.db_manager.execute_query(query, tuple(values))

    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the database"""
        query = "DELETE FROM users WHERE id = %s"
        logging.info(f"Deleting user: {user_id}")
        return self.db_manager.execute_query(query, (user_id,))
