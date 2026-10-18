"""Budget alert and spending insight helpers.

Budget status rules:
- Normal: below 80% of the monthly category budget
- Near limit: from 80% up to but not including 100%
- Over budget: 100% or more

These rules are applied only to actual expense rows. Income rows are never treated
as spending.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd

DEFAULT_SAMPLE_BUDGETS = {
    "Food": 20000,
    "Transport": 15000,
    "Rent": 25000,
    "Shopping": 18000,
    "Healthcare": 10000,
    "Education": 12000,
    "Utilities": 10000,
    "Entertainment": 9000,
    "Other": 5000,
}


def validate_category_budget_map(budgets: Dict[str, float] | None) -> Dict[str, float]:
    """Normalize a user-provided budget map and reject invalid or non-positive values."""
    if budgets is None:
        return {}

    valid_budgets: Dict[str, float] = {}
    for category, value in budgets.items():
        if category is None:
            continue
        category_name = str(category).strip()
        if not category_name:
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        if numeric_value <= 0:
            continue
        valid_budgets[category_name.title()] = numeric_value
    return valid_budgets


def filter_by_month(df: pd.DataFrame, month: str | None = None) -> pd.DataFrame:
    """Filter a dataframe to a selected month in YYYY-MM format when provided."""
    if df is None or df.empty:
        return df.copy() if df is not None else pd.DataFrame()
    if month is None or str(month).strip().lower() in {"", "all", "all months"}:
        return df.copy()

    if "date" not in df.columns:
        return df.copy()

    filtered = df.copy()
    filtered["date"] = pd.to_datetime(filtered["date"], errors="coerce")
    filtered = filtered[filtered["date"].notna()]
    month_key = str(month).strip()
    filtered = filtered[filtered["date"].dt.strftime("%Y-%m") == month_key]
    return filtered


def compute_category_expense_totals(df: pd.DataFrame, month: str | None = None) -> pd.DataFrame:
    """Return expense totals by category for a selected month or for all data."""
    filtered = filter_by_month(df, month)
    if filtered is None or filtered.empty:
        return pd.DataFrame(columns=["category", "expense_total"])

    expense_rows = filtered.loc[filtered["transaction_type"].astype(str).str.title() == "Expense"].copy()
    if expense_rows.empty:
        return pd.DataFrame(columns=["category", "expense_total"])

    totals = (
        expense_rows.groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "expense_total"})
    )
    return totals.sort_values("expense_total", ascending=False).reset_index(drop=True)


def compute_budget_statuses(df: pd.DataFrame, budgets: Dict[str, float] | None = None, month: str | None = None) -> pd.DataFrame:
    """Return category, expense totals, budget, and status for a selected month."""
    valid_budgets = validate_category_budget_map(budgets)
    if not valid_budgets:
        return pd.DataFrame(columns=["category", "expense_total", "budget", "usage_pct", "status"])

    filtered = filter_by_month(df, month)
    totals = compute_category_expense_totals(filtered, month=None)
    if totals.empty:
        return pd.DataFrame(columns=["category", "expense_total", "budget", "usage_pct", "status"])

    rows = []
    for category, budget in valid_budgets.items():
        category_total = totals.loc[totals["category"] == category, "expense_total"]
        expense_total = float(category_total.iloc[0]) if not category_total.empty else 0.0
        usage_pct = (expense_total / budget * 100) if budget > 0 else 0.0

        if usage_pct < 80:
            status = "Normal"
        elif usage_pct < 100:
            status = "Near limit"
        else:
            status = "Over budget"

        rows.append({
            "category": category,
            "expense_total": expense_total,
            "budget": budget,
            "usage_pct": usage_pct,
            "status": status,
        })

    results = pd.DataFrame(rows)
    if results.empty:
        return pd.DataFrame(columns=["category", "expense_total", "budget", "usage_pct", "status"])
    return results.sort_values("usage_pct", ascending=False).reset_index(drop=True)


def calculate_month_over_month_expenses(df: pd.DataFrame) -> pd.DataFrame:
    """Return month-over-month expense changes, only when comparable months exist."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["month_year", "expense_total", "mom_change_pct"])

    expense_rows = df.loc[df["transaction_type"].astype(str).str.title() == "Expense"].copy()
    if expense_rows.empty:
        return pd.DataFrame(columns=["month_year", "expense_total", "mom_change_pct"])

    expense_rows["date"] = pd.to_datetime(expense_rows["date"], errors="coerce")
    expense_rows["month_year"] = expense_rows["date"].dt.to_period("M").astype(str)

    monthly = (
        expense_rows.groupby("month_year", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "expense_total"})
        .sort_values("month_year")
        .reset_index(drop=True)
    )

    if len(monthly) < 2:
        return monthly.assign(mom_change_pct=0.0)

    monthly["mom_change_pct"] = monthly["expense_total"].pct_change().fillna(0.0) * 100
    return monthly


def generate_spending_insights(df: pd.DataFrame, budgets: Dict[str, float] | None = None, month: str | None = None) -> List[str]:
    """Generate safe, factual spending insights based only on actual expense records."""
    if df is None:
        return ["No transaction data is available for spending insights."]

    filtered = filter_by_month(df, month)
    expense_rows = filtered.loc[filtered["transaction_type"].astype(str).str.title() == "Expense"].copy()
    if filtered.empty or expense_rows.empty:
        return ["No expense rows are available for spending insights."]

    insights: List[str] = []

    category_totals = compute_category_expense_totals(expense_rows, month=None)
    if not category_totals.empty:
        highest = category_totals.iloc[0]
        insights.append(
            f"The highest spending category is {highest['category']} with ₹{highest['expense_total']:,.2f} in expenses."
        )

    monthly = calculate_month_over_month_expenses(expense_rows)
    if len(monthly) >= 2:
        last_month = monthly.iloc[-1]
        previous_month = monthly.iloc[-2]
        change = last_month["mom_change_pct"]
        insights.append(
            f"Month-over-month expense change for {last_month['month_year']} compared with {previous_month['month_year']}: {change:.2f}% ."
        )

    status_df = compute_budget_statuses(expense_rows, budgets or DEFAULT_SAMPLE_BUDGETS, month=None)
    if not status_df.empty:
        near_or_over = status_df[status_df["status"].isin(["Near limit", "Over budget"])]
        if not near_or_over.empty:
            lines = []
            for _, row in near_or_over.iterrows():
                lines.append(
                    f"{row['category']} is {row['status']} using {row['usage_pct']:.1f}% of its budget."
                )
            insights.append(" | ".join(lines))

    return insights


def save_insight_summary(df: pd.DataFrame, budgets: Dict[str, float] | None = None, output_path: str | Path | None = None) -> Path | None:
    """Save a machine-readable summary to a CSV report if an output path is provided."""
    if output_path is None:
        return None

    status_df = compute_budget_statuses(df, budgets or DEFAULT_SAMPLE_BUDGETS)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    status_df.to_csv(output, index=False)
    return output


def main() -> None:
    """Demonstrate the insight generator on the cleaned dataset."""
    input_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "expenses_clean.csv"
    df = pd.read_csv(input_path)
    insights = generate_spending_insights(df, DEFAULT_SAMPLE_BUDGETS)
    for insight in insights:
        print(insight)


if __name__ == "__main__":
    main()
