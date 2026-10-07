import argparse
from contextlib import closing
from pathlib import Path
import sqlite3


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[3] / "data" / "orders.sqlite3"


def reset_database(database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("BEGIN")
            connection.execute("DROP TABLE IF EXISTS orders")
            connection.execute("""
                CREATE TABLE orders (
                    id TEXT PRIMARY KEY NOT NULL,
                    customer_name TEXT NOT NULL,
                    total_cents INTEGER NOT NULL
                        CHECK (typeof(total_cents) = 'integer' AND total_cents >= 0),
                    status TEXT NOT NULL
                        CHECK (status IN ('pending', 'processing', 'shipped', 'cancelled'))
                )
            """)
            connection.executemany(
                "INSERT INTO orders (id, customer_name, total_cents, status) VALUES (?, ?, ?, ?)",
                [
                    ("ORD-1001", "Alice", 8450, "pending"),
                    ("ORD-1002", "Bob", 12000, "processing"),
                    ("ORD-1003", "Carol", 3990, "shipped"),
                ],
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore the initial demo orders.")
    parser.add_argument("--path", type=Path, default=DEFAULT_DATABASE_PATH)
    args = parser.parse_args()
    reset_database(args.path)
    print(f"Database reset: {args.path.resolve()}")


if __name__ == "__main__":
    main()
