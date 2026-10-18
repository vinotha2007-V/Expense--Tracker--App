"""Feature engineering helpers for the expense tracker project.

This module adds safe, reproducible derived fields for date-related analysis and
transaction segmentation while preserving the original source columns.
"""

from __future__ import annotations

import pandas as pd


MONTH_NAME_MAP = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add safe date-derived fields without modifying original semantics."""
    result = df.copy()

    if "date" not in result.columns:
        raise ValueError("The dataframe must contain a 'date' column.")

    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result["year"] = result["date"].dt.year
    result["month_number"] = result["date"].dt.month
    result["month_name"] = result["month_number"].map(MONTH_NAME_MAP)
    result["month_year"] = result["date"].dt.to_period("M").astype(str)
    result["day_of_week"] = result["date"].dt.day_name()
    result["is_weekend"] = result["date"].dt.dayofweek.isin([5, 6]).astype(int)
    return result


def add_transaction_direction(df: pd.DataFrame) -> pd.DataFrame:
    """Create a readable income/expense direction field."""
    result = df.copy()
    result["transaction_direction"] = result["transaction_type"].map(
        {"Income": "inflow", "Expense": "outflow"}
    )
    return result


def add_expense_category_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add boolean category flags for common spending groups."""
    result = df.copy()
    categories = [
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
    for category in categories:
        result[f"is_{category.lower()}"] = (
            result["category"].astype(str).str.lower() == category.lower()
        )
    return result


def add_amount_band(df: pd.DataFrame) -> pd.DataFrame:
    """Add a positive-amount transaction band with sensible business-friendly boundaries.

    Boundaries are documented as follows:
    - 0 to 999: Low
    - 1000 to 4999: Medium
    - 5000 to 19999: High
    - 20000 and above: Very high
    """
    result = df.copy()
    result["amount"] = pd.to_numeric(result["amount"], errors="coerce")
    bands = pd.cut(
        result["amount"],
        bins=[0, 999, 4999, 19999, float("inf")],
        labels=["Low", "Medium", "High", "Very High"],
        right=False,
    )
    result["amount_band"] = bands
    return result


def engineer_transaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply a standard set of feature engineering steps while preserving source columns."""
    result = add_date_features(df)
    result = add_transaction_direction(result)
    result = add_expense_category_indicators(result)
    result = add_amount_band(result)
    return result
