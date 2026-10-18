"""Core exploratory data analysis functions for the expense tracker app.

This module computes key financial metrics from the cleaned transaction dataset
without mixing income and expense logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


def ensure_columns(df: pd.DataFrame) -> None:
    """Check required transaction columns before analysis."""
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
        raise ValueError(f"Dataset is missing required columns: {missing}")


def load_cleaned_data(path: str | Path) -> pd.DataFrame:
    """Load the processed dataset and normalize date values."""
    df = pd.read_csv(path)
    ensure_columns(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def safe_sum(series: pd.Series) -> float:
    """Safely sum a pandas series, returning 0.0 for empty input."""
    return float(series.sum()) if len(series) else 0.0


def calculate_summary_metrics(df: pd.DataFrame) -> dict:
    """Compute core summary metrics for income and expense transactions."""
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_savings": 0.0,
            "transaction_count": 0,
            "average_expense": 0.0,
            "median_expense": 0.0,
            "highest_spending_category": None,
            "total_expense_transactions": 0,
        }

    income_total = safe_sum(df.loc[df["transaction_type"] == "Income", "amount"])
    expense_total = safe_sum(df.loc[df["transaction_type"] == "Expense", "amount"])
    expense_values = df.loc[df["transaction_type"] == "Expense", "amount"]

    category_totals = (
        df.loc[df["transaction_type"] == "Expense", ["category", "amount"]]
        .groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "expense_total"})
        .sort_values("expense_total", ascending=False)
    )

    highest_category = None
    if not category_totals.empty:
        highest_category = category_totals.iloc[0]["category"]

    summary = {
        "total_income": income_total,
        "total_expenses": expense_total,
        "net_savings": income_total - expense_total,
        "transaction_count": int(len(df)),
        "average_expense": float(expense_values.mean()) if not expense_values.empty else 0.0,
        "median_expense": float(expense_values.median()) if not expense_values.empty else 0.0,
        "highest_spending_category": highest_category,
        "total_expense_transactions": int(len(expense_values)),
        "category_totals": category_totals,
    }
    return summary


def calculate_category_expense_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Compute expense totals and percentages by category."""
    if df.empty:
        return pd.DataFrame(columns=["category", "expense_total", "percentage_of_expenses"])

    expense_df = df[df["transaction_type"] == "Expense"].copy()
    if expense_df.empty:
        return pd.DataFrame(columns=["category", "expense_total", "percentage_of_expenses"])

    category_totals = (
        expense_df.groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "expense_total"})
    )
    total_expenses = category_totals["expense_total"].sum()
    if total_expenses == 0:
        category_totals["percentage_of_expenses"] = 0.0
    else:
        category_totals["percentage_of_expenses"] = (
            category_totals["expense_total"] / total_expenses * 100
        )
    return category_totals.sort_values("expense_total", ascending=False).reset_index(drop=True)


def calculate_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly income, expenses, and net savings aggregated by month."""
    if df.empty:
        return pd.DataFrame(columns=["month_year", "income_total", "expense_total", "net_savings"])

    df = df.copy()
    df["month_year"] = df["date"].dt.to_period("M").astype(str)

    monthly = (
        df.groupby(["month_year", "transaction_type"], as_index=False)["amount"]
        .sum()
        .pivot(index="month_year", columns="transaction_type", values="amount")
        .fillna(0)
        .reset_index()
    )

    monthly = monthly.rename(columns={"Income": "income_total", "Expense": "expense_total"})
    for col in ["income_total", "expense_total"]:
        if col not in monthly.columns:
            monthly[col] = 0.0

    monthly["net_savings"] = monthly["income_total"] - monthly["expense_total"]
    return monthly[["month_year", "income_total", "expense_total", "net_savings"]].sort_values("month_year")


def calculate_transaction_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Return counts by category and transaction type."""
    if df.empty:
        return pd.DataFrame(columns=["category", "transaction_type", "count"])

    counts = (
        df.groupby(["category", "transaction_type"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    return counts.sort_values(["transaction_type", "count"], ascending=[True, False])


def calculate_summary_report(df: pd.DataFrame) -> Dict[str, object]:
    """Aggregate all EDA metrics into a single dictionary."""
    summary = calculate_summary_metrics(df)
    category_breakdown = calculate_category_expense_breakdown(df)
    monthly_summary = calculate_monthly_summary(df)
    counts = calculate_transaction_counts(df)

    return {
        "summary": summary,
        "category_breakdown": category_breakdown,
        "monthly_summary": monthly_summary,
        "transaction_counts": counts,
    }


def main() -> None:
    """Load the cleaned CSV and print a concise EDA summary."""
    input_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "expenses_clean.csv"
    df = load_cleaned_data(input_path)
    report = calculate_summary_report(df)

    print("TOTAL_INCOME", round(report["summary"]["total_income"], 2))
    print("TOTAL_EXPENSES", round(report["summary"]["total_expenses"], 2))
    print("NET_SAVINGS", round(report["summary"]["net_savings"], 2))
    print("AVERAGE_EXPENSE", round(report["summary"]["average_expense"], 2))
    print("MEDIAN_EXPENSE", round(report["summary"]["median_expense"], 2))
    print(report["category_breakdown"].head().to_string(index=False))
    print(report["monthly_summary"].head().to_string(index=False))


if __name__ == "__main__":
    main()
