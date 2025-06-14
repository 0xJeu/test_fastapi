import argparse
import logging
import sys

from db.core import DatabaseManager

# Configure logging for this script
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def initialize_database(db_manager: DatabaseManager) -> bool:
    """Initialize the database and create tables with sample data."""
    logging.info("Initializing database...")
    success = db_manager.initialize_database()

    if success:
        logging.info("✅ Database initialization completed successfully.")
        logging.info("📊 Sample users have been added to the database.")
    else:
        logging.error("❌ Database initialization failed.")

    return success


def clean_and_reinitialize(db_manager: DatabaseManager, args) -> bool:
    """Clean the existing database and reinitialize it."""
    # Check if database exists and has data
    users = db_manager.users.get_all_users()
    products = db_manager.products.get_all_products()
    if users:
        if not args.force:
            logging.warning(
                f"🧹 Cleaning database with {len(users)} existing users - "
                "this will delete all data!"
            )
        else:
            logging.warning(f"🧹 Cleaning database with {len(users)} existing users")
    if products:
        if not args.force:
            logging.warning(
                f"🧹 Cleaning database with {len(products)} existing products - "
                "this will delete all data!"
            )
        else:
            logging.warning(
                f"🧹 Cleaning database with {len(products)} existing products"
            )
    else:
        logging.warning(
            "🧹 No existing database found - proceeding with initialization."
        )

    # Ask for confirmation
    try:
        if not args.force:
            confirm = (
                input("Are you sure you want to proceed? (yes/no): ").lower().strip()
            )
            if confirm not in ["yes", "y"]:
                logging.info("Operation cancelled by user.")
                return False
    except KeyboardInterrupt:
        logging.info("\nOperation cancelled by user.")
        return False

    success = db_manager.clean_db()

    if success:
        logging.info("✅ Database cleaned and reinitialized successfully.")
        logging.info("📊 Fresh sample users have been loaded.")
        logging.info("📊 Fresh sample products have been loaded.")
    else:
        logging.error("❌ Database cleaning failed.")

    return success


def check_database_status(db_manager: DatabaseManager) -> None:
    """Check the current status of the database."""
    logging.info("🔍 Checking database status...")

    try:
        users = db_manager.users.get_all_users()
        products = db_manager.products.get_all_products()
        if users:
            logging.info(f"📈 Database is active with {len(users)} users:")
            for user in users[:3]:  # Show first 3 users
                logging.info(f"   - {user['name']} ({user['email']})")
            if len(users) > 3:
                logging.info(f"   ... and {len(users) - 3} more users")
        if products:
            logging.info(f"📈 Database is active with {len(products)} products:")
            for product in products[:3]:  # Show first 3 products
                logging.info(f"   - {product['name']} ({product['description']})")
            if len(products) > 3:
                logging.info(f"   ... and {len(products) - 3} more products")
        else:
            logging.info("📭 Database is empty or not initialized.")

    except Exception as e:
        logging.error(f"❌ Could not connect to database: {e}")


def main():
    """Main function to handle database operations."""
    parser = argparse.ArgumentParser(
        description="Database initialization and management script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
    uv run python init_db.py                    # Initialize database
    uv run python init_db.py --clean            # Clean and reinitialize
    uv run python init_db.py --status           # Check database status
    uv run python init_db.py --clean --status   # Clean and show status
        """,
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean and reinitialize the database (removes all data)",
    )

    parser.add_argument(
        "--status", action="store_true", help="Check the current status of the database"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt and proceed with operation",
    )

    args = parser.parse_args()

    try:
        # Initialize the database manager from environment variables
        db = DatabaseManager.from_env()

        logging.info(f"🔗 Connecting to: {db.user}@{db.host}:{db.port}/{db.database}")

        # Perform requested operations
        if args.clean:
            success = clean_and_reinitialize(db, args)
            if not success:
                sys.exit(1)
        elif not args.status:
            # Default action: initialize database
            success = initialize_database(db)
            if not success:
                sys.exit(1)

        if args.status:
            check_database_status(db)

    except ValueError as e:
        logging.error(f"❌ Configuration error: {e}")
        logging.error("💡 Make sure your .env file is properly configured.")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("\n👋 Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
