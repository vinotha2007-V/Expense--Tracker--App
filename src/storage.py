"""SQLite storage layer for the Expense Tracker App.

This module provides a lightweight persistent store for transactions using the
standard library sqlite3 module. It does not import data automatically at module
load time and it keeps SQL parameterized for safety.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "expenses.db"


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection for the given database."""
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: str | Path = DB_PATH) -> None:
    """Create the transactions table if it does not already exist."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL CHECK(transaction_type IN ('Income', 'Expense')),
                payment_method TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_transaction(
    transaction: dict,
    db_path: str | Path = DB_PATH,
) -> bool:
    """Insert one transaction if transaction_id is unique; return True on success."""
    required = {
        "transaction_id",
        "date",
        "description",
        "category",
        "amount",
        "transaction_type",
        "payment_method",
    }
    missing = sorted(required - set(transaction.keys()))
    if missing:
        raise ValueError(f"Transaction is missing required fields: {missing}")

    with get_connection(db_path) as conn:
        try:
            conn.execute(
                """
                INSERT INTO transactions (
                    transaction_id, date, description, category, amount,
                    transaction_type, payment_method
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction["transaction_id"],
                    str(transaction["date"]),
                    str(transaction["description"]),
                    str(transaction["category"]),
                    float(transaction["amount"]),
                    str(transaction["transaction_type"]),
                    str(transaction["payment_method"]),
                ),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_transactions(db_path: str | Path = DB_PATH) -> List[dict]:
    """Return all rows in the transactions table as a list of dictionaries."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT transaction_id, date, description, category, amount, transaction_type, payment_method FROM transactions ORDER BY date"
        ).fetchall()
    return [dict(row) for row in rows]


def transaction_exists(transaction_id: str, db_path: str | Path = DB_PATH) -> bool:
    """Check whether a transaction_id already exists in the database."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM transactions WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchone()
    return row is not None


def import_csv_transactions(
    csv_path: str | Path,
    db_path: str | Path = DB_PATH,
) -> dict:
    """Load a CSV file into the SQLite table without duplicating existing records.

    Returns a summary dictionary with inserted and skipped counts.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    required = {
        "transaction_id",
        "date",
        "description",
        "category",
        "amount",
        "transaction_type",
        "payment_method",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    initialize_database(db_path)
    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        record = row.to_dict()
        if transaction_exists(record["transaction_id"], db_path):
            skipped += 1
            continue
        if insert_transaction(record, db_path):
            inserted += 1
        else:
            skipped += 1

    return {"inserted": inserted, "skipped": skipped, "total_seen": len(df)}


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {DB_PATH}")
