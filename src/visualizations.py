"""Visualization helpers for the expense tracker project.

This module creates readable charts from the cleaned transaction dataset and saves
PNG files to the outputs/figures directory.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def format_inr(value: float) -> str:
    """Return a readable INR-style label for chart formatting."""
    return f"₹{value:,.0f}"


def load_data(path: str | Path) -> pd.DataFrame:
    """Load the processed dataset and ensure dates are parsed."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def save_expense_distribution_chart(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Save an expense distribution chart by category."""
    expense_df = df[df["transaction_type"] == "Expense"].copy()
    if expense_df.empty:
        raise ValueError("No expense rows available for plotting.")

    category_totals = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=category_totals.values, y=category_totals.index, palette="viridis", ax=ax)
    ax.set_title("Expense Distribution by Category")
    ax.set_xlabel("Amount (INR)")
    ax.set_ylabel("Category")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: format_inr(x)))
    fig.tight_layout()

    path = Path(output_path) if output_path else OUTPUT_DIR / "expense_distribution_by_category.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def save_monthly_income_expense_chart(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Save a monthly income versus expense trend chart."""
    monthly = df.copy()
    monthly["month_year"] = monthly["date"].dt.to_period("M").astype(str)
    monthly = (
        monthly.groupby(["month_year", "transaction_type"], as_index=False)["amount"]
        .sum()
        .pivot(index="month_year", columns="transaction_type", values="amount")
        .fillna(0)
        .reset_index()
    )
    if "Income" not in monthly.columns:
        monthly["Income"] = 0.0
    if "Expense" not in monthly.columns:
        monthly["Expense"] = 0.0

    monthly = monthly[["month_year", "Income", "Expense"]].sort_values("month_year")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(monthly["month_year"], monthly["Income"], marker="o", linewidth=2, label="Income")
    ax.plot(monthly["month_year"], monthly["Expense"], marker="o", linewidth=2, label="Expense")
    ax.set_title("Monthly Income vs Expenses")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (INR)")
    ax.legend()
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: format_inr(x)))
    fig.tight_layout()

    path = Path(output_path) if output_path else OUTPUT_DIR / "monthly_income_vs_expenses.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def save_monthly_net_savings_chart(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Save the monthly net savings trend chart."""
    monthly = df.copy()
    monthly["month_year"] = monthly["date"].dt.to_period("M").astype(str)
    monthly = (
        monthly.groupby(["month_year", "transaction_type"], as_index=False)["amount"]
        .sum()
        .pivot(index="month_year", columns="transaction_type", values="amount")
        .fillna(0)
        .reset_index()
    )
    if "Income" not in monthly.columns:
        monthly["Income"] = 0.0
    if "Expense" not in monthly.columns:
        monthly["Expense"] = 0.0
    monthly["net_savings"] = monthly["Income"] - monthly["Expense"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(monthly["month_year"], monthly["net_savings"], marker="o", color="green", linewidth=2)
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.set_title("Monthly Net Savings")
    ax.set_xlabel("Month")
    ax.set_ylabel("Net Savings (INR)")
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: format_inr(x)))
    fig.tight_layout()

    path = Path(output_path) if output_path else OUTPUT_DIR / "monthly_net_savings.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def save_income_vs_expense_summary_chart(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Save a simple summary bar chart comparing total income and total expenses."""
    income_total = df.loc[df["transaction_type"] == "Income", "amount"].sum()
    expense_total = df.loc[df["transaction_type"] == "Expense", "amount"].sum()

    figure_data = pd.DataFrame(
        {"category": ["Income", "Expenses"], "amount": [income_total, expense_total]}
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=figure_data, x="category", y="amount", palette=["#2ca02c", "#d62728"], ax=ax)
    ax.set_title("Income vs Expenses Summary")
    ax.set_xlabel("Type")
    ax.set_ylabel("Amount (INR)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: format_inr(x)))
    fig.tight_layout()

    path = Path(output_path) if output_path else OUTPUT_DIR / "income_vs_expenses_summary.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def main() -> None:
    """Generate all EDA charts from the cleaned dataset."""
    input_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "expenses_clean.csv"
    df = load_data(input_path)
    save_expense_distribution_chart(df)
    save_monthly_income_expense_chart(df)
    save_monthly_net_savings_chart(df)
    save_income_vs_expense_summary_chart(df)
    print("EDA charts saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
