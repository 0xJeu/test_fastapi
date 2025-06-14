import logging

import uvicorn
from fastapi import FastAPI

from routes.posts import router as posts_router
from routes.product import router as products_router
from routes.users import router as users_router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="FastAPI DB Application",
    description="FastAPI application with MySQL database integration",
    version="0.1.0",
)

app.include_router(users_router)
app.include_router(products_router)
app.include_router(posts_router)


@app.get("/")
def read_root():
    """Root endpoint providing API information and health status."""
    return {
        "message": "Welcome to FastAPI DB Application",
        "description": "FastAPI application with MySQL database integration",
        "version": "0.1.0",
        "status": "healthy",
        "main endpoints": {
            "users": "/users",
            "products": "/products",
            "posts": "/posts",
        },
        "documentation": {
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
