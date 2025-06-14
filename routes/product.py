import logging

from fastapi import APIRouter
from pydantic import BaseModel

from db.core import DatabaseManager

router = APIRouter(prefix="/products", tags=["products"])

db = DatabaseManager.from_env()


class Product(BaseModel):
    name: str
    description: str
    price: float
    quantity: int


@router.get("/")
def list_products():
    products = db.products.get_all_products()
    logging.info(f"Product Size: {len(products)}")
    for product in products:
        logging.info(f"Product: {product}")
    return {"Products": products}


@router.get("/{product_id}")
def get_product(product_id: int):
    logging.info(f"Getting product by ID: {product_id}")
    product = db.products.get_product(product_id)
    return {"Product": product}


@router.post("/")
def create_product(product: Product):
    logging.info(
        f"Creating product: {product.name}, {product.description}, {product.price}, {product.quantity}"
    )
    db.products.create_product(
        product.name, product.description, product.price, product.quantity
    )
    return {"message": "Product created"}


@router.put("/{product_id}")
def update_product(product_id: int, product: Product):
    logging.info(
        f"Updating product: {product_id}, {product.name}, {product.description}, {product.price}, {product.quantity}"
    )
    db.products.update_product(
        product_id, product.name, product.description, product.price, product.quantity
    )
    return {"message": "Product updated"}


@router.delete("/{product_id}")
def delete_product(product_id: int):
    logging.info(f"Deleting product: {product_id}")
    db.products.delete_product(product_id)
    return {"message": "Product deleted"}
