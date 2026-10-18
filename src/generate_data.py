"""Generate synthetic income and expense transactions for the Expense Tracker App.

This script creates a reproducible dataset with 1,000 transactions and writes it to
`data/raw/expenses.csv`. The data is synthetic and intended only for learning,
analysis, and portfolio demonstration.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_TRANSACTIONS = 1000
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "expenses.csv"

CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Shopping",
    "Healthcare",
    "Education",
    "Utilities",
    "Entertainment",
    "Salary",
    "Other",
]

PAYMENT_METHODS = ["UPI", "Cash", "Debit Card", "Credit Card", "Bank Transfer", "Net Banking"]
TRANSACTION_TYPES = ["Expense", "Income"]


def generate_transactions(n_rows: int = N_TRANSACTIONS, seed: int = SEED) -> pd.DataFrame:
    """Create synthetic financial transactions with realistic structure."""
    rng = np.random.default_rng(seed)

    start_date = pd.Timestamp("2023-01-01")
    end_date = pd.Timestamp("2025-12-31")
    days = (end_date - start_date).days

    transaction_ids = [f"TXN-{i:04d}" for i in range(1, n_rows + 1)]
    dates = pd.to_datetime(
        start_date + pd.to_timedelta(rng.integers(0, days + 1, size=n_rows), unit="D")
    )

    descriptions = [
        "Groceries",
        "Office commute",
        "Monthly rent",
        "Online shopping",
        "Doctor consultation",
        "Course fee",
        "Electricity bill",
        "Movie tickets",
        "Monthly salary",
        "Miscellaneous purchase",
        "Lunch meeting",
        "Fuel refill",
        "Household utilities",
        "Streaming subscription",
        "Freelance payment",
    ]

    transaction_type = rng.choice(TRANSACTION_TYPES, size=n_rows, p=[0.7, 0.3])

    expense_category_pool = [
        "Food",
        "Transport",
        "Rent",
        "Shopping",
        "Healthcare",
        "Education",
        "Utilities",
        "Entertainment",
        "Other",
    ]

    category = np.empty(n_rows, dtype=object)
    income_mask = transaction_type == "Income"
    category[income_mask] = "Salary"
    category[~income_mask] = rng.choice(expense_category_pool, size=int((~income_mask).sum()))

    amount = np.abs(rng.normal(loc=0, scale=1, size=n_rows))
    amount = np.where(transaction_type == "Income", amount * 30000 + 20000, amount * 3500 + 250)
    amount = np.round(amount, 2)

    payment_method = rng.choice(PAYMENT_METHODS, size=n_rows)

    df = pd.DataFrame(
        {
            "transaction_id": transaction_ids,
            "date": dates,
            "description": [
                descriptions[i % len(descriptions)] for i in range(n_rows)
            ],
            "category": category,
            "amount": amount,
            "transaction_type": transaction_type,
            "payment_method": payment_method,
        }
    )

    df["description"] = df["description"].str.title()
    df["category"] = df["category"].astype(str)
    df["payment_method"] = df["payment_method"].astype(str)

    return df


def save_transactions(df: pd.DataFrame, output_path: str | Path = OUTPUT_PATH) -> Path:
    """Save the dataset to CSV after ensuring the directory exists."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def main() -> None:
    """Generate and save the synthetic dataset."""
    df = generate_transactions()
    output = save_transactions(df)
    print(f"Generated synthetic dataset with {len(df)} rows at {output}")


if __name__ == "__main__":
    main()
