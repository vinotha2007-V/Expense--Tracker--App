import sqlite3

import pandas as pd
import pytest

from src.storage import get_connection, import_csv_transactions, initialize_database, insert_transaction, transaction_exists


@pytest.fixture
def temp_db_path(tmp_path):
    db_path = tmp_path / "test_expenses.db"
    initialize_database(db_path)
    return db_path


def test_initialize_database_creates_table(temp_db_path):
    with get_connection(temp_db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
        ).fetchall()
    assert len(tables) == 1


def test_insert_and_retrieve_transaction(temp_db_path):
    row = {
        "transaction_id": "TXN-TEST-1",
        "date": "2024-02-01",
        "description": "Groceries",
        "category": "Food",
        "amount": 1350.50,
        "transaction_type": "Expense",
        "payment_method": "UPI",
    }

    result = insert_transaction(row, temp_db_path)
    assert result is True
    assert transaction_exists("TXN-TEST-1", temp_db_path) is True

    with get_connection(temp_db_path) as conn:
        stored = conn.execute(
            "SELECT transaction_id, category, amount FROM transactions WHERE transaction_id = ?",
            ("TXN-TEST-1",),
        ).fetchone()

    assert stored is not None
    assert stored[0] == "TXN-TEST-1"
    assert stored[1] == "Food"
    assert float(stored[2]) == pytest.approx(1350.50)


def test_duplicate_transaction_id_is_rejected(temp_db_path):
    row = {
        "transaction_id": "TXN-TEST-2",
        "date": "2024-02-02",
        "description": "Salary",
        "category": "Salary",
        "amount": 55000.0,
        "transaction_type": "Income",
        "payment_method": "Bank Transfer",
    }

    assert insert_transaction(row, temp_db_path) is True
    assert insert_transaction(row, temp_db_path) is False


def test_import_csv_transactions_skips_duplicates(temp_db_path):
    csv_path = temp_db_path.with_suffix(".csv")
    df = pd.DataFrame(
        [
            {
                "transaction_id": "TXN-CSV-1",
                "date": "2024-03-01",
                "description": "Rent",
                "category": "Rent",
                "amount": 18000.0,
                "transaction_type": "Expense",
                "payment_method": "Bank Transfer",
            },
            {
                "transaction_id": "TXN-CSV-2",
                "date": "2024-03-02",
                "description": "Salary",
                "category": "Salary",
                "amount": 40000.0,
                "transaction_type": "Income",
                "payment_method": "UPI",
            },
        ]
    )
    df.to_csv(csv_path, index=False)

    summary = import_csv_transactions(csv_path, temp_db_path)
    assert summary["inserted"] == 2
    assert summary["skipped"] == 0

    duplicate_summary = import_csv_transactions(csv_path, temp_db_path)
    assert duplicate_summary["inserted"] == 0
    assert duplicate_summary["skipped"] == 2
