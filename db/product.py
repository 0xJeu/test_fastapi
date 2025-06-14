import logging
from typing import Dict, List, Optional


class ProductCRUD:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_products(self) -> List[Dict]:
        query = "SELECT * FROM products"
        logging.info("Getting all products")
        return self.db_manager.fetch_all(query)

    def get_product(self, product_id: int) -> Optional[Dict]:
        query = "SELECT * FROM products WHERE id = %s"
        logging.info(f"Getting product by ID: {product_id}")
        return self.db_manager.fetch_one(query, (product_id,))

    def create_product(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
        is_admin: bool = False,
    ) -> bool:
        if not is_admin:
            logging.warning(
                "Unauthorized attempt to create product - admin access required"
            )
            raise PermissionError("Admin access required to create products")

        query = "INSERT INTO products (name, description, price, quantity) VALUES (%s, %s, %s, %s)"
        logging.info(f"Creating product: {name}, {description}, {price}, {quantity}")
        return self.db_manager.execute_query(
            query, (name, description, price, quantity)
        )

    def update_product(
        self, product_id: int, name: str, description: str, price: float, quantity: int
    ) -> bool:
        query = "UPDATE products SET name = %s, description = %s, price = %s, quantity = %s WHERE id = %s"
        logging.info(
            f"Updating product: {product_id}, {name}, {description}, {price}, {quantity}"
        )
        return self.db_manager.execute_query(
            query, (name, description, price, quantity, product_id)
        )

    def delete_product(self, product_id: int) -> bool:
        query = "DELETE FROM products WHERE id = %s"
        logging.info(f"Deleting product: {product_id}")
        return self.db_manager.execute_query(query, (product_id,))
