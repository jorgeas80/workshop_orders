from pathlib import Path

from fastapi import FastAPI

from .api.orders import create_orders_router
from .infrastructure.database import DEFAULT_DATABASE_PATH
from .infrastructure.sqlite_order_repository import SQLiteOrderRepository


def create_app(database_path: str | Path = DEFAULT_DATABASE_PATH) -> FastAPI:
    repository = SQLiteOrderRepository(database_path)
    app = FastAPI(title="Workshop Orders")
    app.include_router(create_orders_router(repository))
    return app


app = create_app()
