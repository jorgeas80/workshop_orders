PYTHON = backend/.venv/bin/python
DB_PATH = backend/data/orders.sqlite3

.PHONY: reset-db
reset-db:
	PYTHONPATH=backend/src "$(PYTHON)" -B -m orders_app.infrastructure.database --path "$(DB_PATH)"
