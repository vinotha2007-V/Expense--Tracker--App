import pandas as pd
import pytest

from src.insights import (
    DEFAULT_SAMPLE_BUDGETS,
    calculate_month_over_month_expenses,
    compute_budget_statuses,
    compute_category_expense_totals,
    generate_spending_insights,
    validate_category_budget_map,
)


def sample_df():
    return pd.DataFrame(
        {
            "transaction_id": ["TXN-1", "TXN-2", "TXN-3", "TXN-4", "TXN-5"],
            "date": [
                "2024-01-05",
                "2024-01-10",
                "2024-02-02",
                "2024-02-15",
                "2024-02-20",
            ],
            "description": ["Groceries", "Train fare", "Rent", "Movie", "Salary"],
            "category": ["Food", "Transport", "Rent", "Entertainment", "Salary"],
            "amount": [500.0, 600.0, 12000.0, 1500.0, 80000.0],
            "transaction_type": ["Expense", "Expense", "Expense", "Expense", "Income"],
            "payment_method": ["UPI", "Cash", "Bank Transfer", "UPI", "Bank Transfer"],
        }
    )


def test_validate_category_budget_map_filters_invalid_values():
    budgets = {"Food": 1000, "Invalid": -50, "": 700, None: 100, "Transport": "950"}
    cleaned = validate_category_budget_map(budgets)
    assert cleaned == {"Food": 1000.0, "Transport": 950.0}


def test_compute_category_expense_totals_excludes_income():
    df = sample_df()
    totals = compute_category_expense_totals(df)
    assert totals["expense_total"].sum() == pytest.approx(14600.0)
    assert "Salary" not in totals["category"].values


def test_compute_budget_statuses_classifies_statuses():
    df = sample_df()
    budgets = {"Food": 1000, "Transport": 500, "Rent": 10000, "Entertainment": 2000}
    status_df = compute_budget_statuses(df, budgets)

    assert (status_df["status"] == "Normal").any()
    assert (status_df["status"] == "Near limit").any() or (status_df["status"] == "Over budget").any()
    assert "Salary" not in status_df["category"].values


def test_generate_spending_insights_handles_empty_data():
    assert generate_spending_insights(pd.DataFrame(columns=["transaction_type"])) == ["No expense rows are available for spending insights."]


def test_calculate_month_over_month_expenses_ignores_income():
    df = sample_df()
    monthly = calculate_month_over_month_expenses(df)
    assert monthly["expense_total"].sum() == pytest.approx(14600.0)
    assert monthly["month_year"].tolist() == ["2024-01", "2024-02"]


def test_compute_budget_statuses_uses_selected_month_only():
    df = sample_df()
    status_df = compute_budget_statuses(df, {"Food": 1000, "Transport": 1000, "Rent": 10000, "Entertainment": 2000}, month="2024-01")
    status_map = status_df.set_index("category")["expense_total"].to_dict()
    assert status_map["Food"] == pytest.approx(500.0)
    assert status_map["Transport"] == pytest.approx(600.0)
    assert status_map["Rent"] == pytest.approx(0.0)
    assert status_map["Entertainment"] == pytest.approx(0.0)


def test_default_sample_budgets_are_available():
    assert "Food" in DEFAULT_SAMPLE_BUDGETS
    assert DEFAULT_SAMPLE_BUDGETS["Food"] > 0
