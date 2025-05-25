import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


class UserCRUD:
    def __init__(self, db_manager: "DatabaseManager"):
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


class DatabaseManager:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.users = UserCRUD(self)  # Initialize UserCRUD

    @classmethod
    def from_env(cls):
        """Create a DatabaseManager instance from environment variables"""
        load_dotenv()  # Load .env file

        # Get values from environment variables - no defaults
        host = os.getenv("DB_HOST")
        port_str = os.getenv("DB_PORT")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME")

        # Validate that all required fields are provided
        if not host:
            raise ValueError("DB_HOST environment variable must be set")
        if not port_str:
            raise ValueError("DB_PORT environment variable must be set")
        if not user:
            raise ValueError("DB_USER environment variable must be set")
        if not password:
            raise ValueError("DB_PASSWORD environment variable must be set")
        if not database:
            raise ValueError("DB_NAME environment variable must be set")

        try:
            port = int(port_str)
        except ValueError:
            raise ValueError("DB_PORT must be a valid integer") from None

        return cls(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )

    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            logging.info(f"Connected to MySQL: {connection}")
            return connection
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            return None

    def execute_query(self, query: str, params: Tuple = None) -> bool:
        """Execute a query that doesn't return data (INSERT, UPDATE, DELETE)"""
        logging.info(f"Executing query: {query}")
        logging.info(f"Params: {params}")
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            return True
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def fetch_one(self, query: str, params: Tuple = None) -> Optional[Dict]:
        """Execute a query and return a single result"""
        connection = self.get_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            logging.error(f"Error fetching data: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def fetch_all(self, query: str, params: Tuple = None) -> List[Dict]:
        """Execute a query and return all results"""
        connection = self.get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            logging.error(f"Error fetching data: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    # Database initialization
    def initialize_database(self):
        """Create the database and tables if they don't exist"""
        try:
            # Connect without specifying database
            connection = mysql.connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Create database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                cursor.execute(f"USE {self.database}")

                # Create users table
                create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
                """
                load_db_data = """
                INSERT INTO users (name, email, password) VALUES
                    ('John Doe', 'john.doe@example.com', 
                     CONCAT(SUBSTRING(MD5(RAND()), 1, 8), 
                            SUBSTRING(MD5(RAND()), 1, 8))),
                    ('Jane Smith', 'jane.smith@example.com', 
                     CONCAT(SUBSTRING(MD5(RAND()), 1, 8), 
                            SUBSTRING(MD5(RAND()), 1, 8))),
                    ('Bob Johnson', 'bob.johnson@example.com', 
                     CONCAT(SUBSTRING(MD5(RAND()), 1, 8), 
                            SUBSTRING(MD5(RAND()), 1, 8))),
                    ('Alice Brown', 'alice.brown@example.com', 
                     CONCAT(SUBSTRING(MD5(RAND()), 1, 8), 
                            SUBSTRING(MD5(RAND()), 1, 8))),
                    ('Charlie Wilson', 'charlie.wilson@example.com', 
                     CONCAT(SUBSTRING(MD5(RAND()), 1, 8), 
                            SUBSTRING(MD5(RAND()), 1, 8)))
                ON DUPLICATE KEY UPDATE name=VALUES(name);
                """
                cursor.execute(create_users_table)
                cursor.execute(load_db_data)
                connection.commit()  # Commit the transaction to save the data

                logging.info("Database initialized successfully")
                return True
        except Error as e:
            logging.error(f"Error initializing database: {e}")
            return False
        finally:
            if "connection" in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def clean_db(self):
        """Clean the database and initialize it again"""
        try:
            # Connect without specifying database
            connection = mysql.connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
                connection.commit()
                logging.info(f"Database: {self.database} dropped")

                # Now reinitialize
                initialize_success = self.initialize_database()
                return initialize_success
        except Error as e:
            logging.error(f"Error cleaning database: {e}")
            return False
        finally:
            if "connection" in locals() and connection.is_connected():
                cursor.close()
                connection.close()
