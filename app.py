from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import calculate_monthly_summary
from src.insights import DEFAULT_SAMPLE_BUDGETS, compute_budget_statuses, filter_by_month, generate_spending_insights
from src.storage import initialize_database

DATA_PATH = Path(__file__).resolve().parent / "data" / "processed" / "expenses_clean.csv"


@st.cache_data
def load_transactions() -> pd.DataFrame:
    """Load the cleaned transaction dataset with safe date parsing."""
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def format_inr(value: float | int) -> str:
    """Format a number as Indian Rupees for display."""
    return f"₹{float(value):,.2f}"


def main() -> None:
    """Render a beginner-friendly Streamlit dashboard for the synthetic expense tracker."""
    initialize_database()

    st.set_page_config(page_title="Expense Tracker App", page_icon="💰", layout="wide")
    st.title("Expense Tracker App")
    st.caption("Synthetic financial data for learning, analysis, and portfolio demonstration only.")

    df = load_transactions()
    if df.empty:
        st.warning("No transaction data is available to display.")
        return

    months = ["All months"] + sorted(df["date"].dt.strftime("%Y-%m").dropna().unique().tolist())
    selected_month = st.selectbox("Select month", months)
    selected_month_value = None if selected_month == "All months" else selected_month

    category_options = ["All categories"] + sorted(df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("Select category", category_options)

    type_options = ["All types", "Income", "Expense"]
    selected_type = st.selectbox("Select transaction type", type_options)

    filtered = df.copy()
    if selected_month_value is not None:
        filtered = filter_by_month(filtered, selected_month_value)
    if selected_category != "All categories":
        filtered = filtered[filtered["category"] == selected_category]
    if selected_type != "All types":
        filtered = filtered[filtered["transaction_type"] == selected_type]

    if filtered.empty:
        st.info("No transactions match the current filters. Please choose a different month, category, or transaction type.")
        return

    income_total = float(filtered.loc[filtered["transaction_type"] == "Income", "amount"].sum())
    expense_total = float(filtered.loc[filtered["transaction_type"] == "Expense", "amount"].sum())
    net_savings = income_total - expense_total

    col1, col2, col3 = st.columns(3)
    col1.metric("Income", format_inr(income_total))
    col2.metric("Expenses", format_inr(expense_total))
    col3.metric("Net savings", format_inr(net_savings))

    st.subheader("Expense by category")
    expense_by_category = (
        filtered.loc[filtered["transaction_type"] == "Expense"]
        .groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )
    if expense_by_category.empty:
        st.info("No expense rows are available for the current selection.")
    else:
        st.bar_chart(expense_by_category.set_index("category")["amount"])

    monthly_summary = calculate_monthly_summary(df)
    if not monthly_summary.empty:
        st.subheader("Monthly income vs expenses")
        st.line_chart(monthly_summary.set_index("month_year")[["income_total", "expense_total"]])

    st.subheader("Budget status by category")
    budget_df = compute_budget_statuses(
        filtered,
        DEFAULT_SAMPLE_BUDGETS,
    )
    if budget_df.empty:
        st.info("No category budget data is available for the selected period.")
    else:
        st.dataframe(
            budget_df[["category", "expense_total", "budget", "usage_pct", "status"]].assign(
                expense_total=lambda x: x["expense_total"].map(lambda value: format_inr(value)),
                budget=lambda x: x["budget"].map(lambda value: format_inr(value)),
                usage_pct=lambda x: x["usage_pct"].map(lambda value: f"{value:.1f}%"),
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Spending insights")
    insights = generate_spending_insights(df, DEFAULT_SAMPLE_BUDGETS, month=selected_month_value)
    if insights:
        for insight in insights:
            st.write(f"- {insight}")

    st.subheader("Transaction table")
    table_df = filtered[["transaction_id", "date", "description", "category", "amount", "transaction_type", "payment_method"]].copy()
    table_df["amount"] = table_df["amount"].map(lambda value: format_inr(value))
    table_df["date"] = table_df["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(table_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
