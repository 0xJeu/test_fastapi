"""
Core database module - imports and re-exports all database functionality.

This module maintains backward compatibility by importing all classes
from their respective modules and making them available as if they
were defined in this file.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

from .posts import PostCRUD
from .product import ProductCRUD
from .users import UserCRUD


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
        self.posts = PostCRUD(self)  # Initialize PostCRUD
        self.products = ProductCRUD(self)  # Initialize ProductCRUD

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

                create_posts_table = """
                CREATE TABLE IF NOT EXISTS posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    user_id INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """

                create_products_table = """
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    quantity INT NOT NULL
                )
                """

                load_posts_db_data = """
                INSERT INTO posts (title, content, user_id) VALUES
                    ('My Journey with FastAPI', 'John shares his experience building scalable APIs with FastAPI and the lessons learned along the way', 1),
                    ('Designing User-Centric Databases', 'Jane discusses her approach to creating database schemas that prioritize user experience and performance', 2),
                    ('Advanced Python Patterns I Use Daily', 'Bob reveals the Python techniques and patterns that have transformed his development workflow', 3),
                    ('Building Modern Web Apps: My Story', 'Alice walks through her process of creating full-stack applications using cutting-edge technologies', 4),
                    ('How I Secure My APIs', 'Charlie explains his comprehensive approach to API security and the tools he relies on', 1),
                """

                load_users_db_data = """
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
                load_products_db_data = """
                INSERT INTO products (name, description, price, quantity) VALUES
                    ('MacBook Pro 16 inch', 'Apple MacBook Pro with M3 chip, 16GB RAM, 512GB SSD', 2499.00, 25),
                    ('Dell XPS 13', 'Ultra-portable laptop with Intel i7, 16GB RAM, 1TB SSD', 1299.00, 40),
                    ('iPhone 15 Pro', 'Latest iPhone with A17 Pro chip, 128GB storage, Titanium design', 999.00, 75),
                    ('Samsung Galaxy S24', 'Android flagship with 256GB storage and advanced camera system', 899.00, 60),
                    ('Sony WH-1000XM5', 'Premium noise-canceling wireless headphones', 399.00, 120)
                """
                load_posts_db_data = """
                INSERT INTO posts (title, content, user_id) VALUES
                    ('My Journey with FastAPI', 'John shares his experience building scalable APIs with FastAPI and the lessons learned along the way', 1),
                    ('Designing User-Centric Databases', 'Jane discusses her approach to creating database schemas that prioritize user experience and performance', 1),
                    ('Advanced Python Patterns I Use Daily', 'Bob reveals the Python techniques and patterns that have transformed his development workflow', 3),
                    ('Building Modern Web Apps: My Story', 'Alice walks through her process of creating full-stack applications using cutting-edge technologies', 4),
                    ('How I Secure My APIs', 'Charlie explains his comprehensive approach to API security and the tools he relies on', 1)
                """
                cursor.execute(create_users_table)
                cursor.execute(create_posts_table)
                cursor.execute(create_products_table)
                cursor.execute(load_users_db_data)
                cursor.execute(load_products_db_data)
                cursor.execute(load_posts_db_data)
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


# Re-export for backward compatibility
__all__ = ["DatabaseManager", "UserCRUD", "PostCRUD"]
