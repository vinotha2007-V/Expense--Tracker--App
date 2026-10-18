import pandas as pd

from src.feature_engineering import engineer_transaction_features


def test_engineer_transaction_features_adds_expected_columns():
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN-0001", "TXN-0002"],
            "date": ["2024-01-01", "2024-01-02"],
            "description": ["Groceries", "Salary payment"],
            "category": ["Food", "Salary"],
            "amount": [1500.0, 45000.0],
            "transaction_type": ["Expense", "Income"],
            "payment_method": ["UPI", "Bank Transfer"],
        }
    )

    result = engineer_transaction_features(df)

    assert {"year", "month_number", "month_name", "month_year", "day_of_week", "is_weekend", "amount_band"}.issubset(result.columns)
    assert result["transaction_id"].tolist() == ["TXN-0001", "TXN-0002"]
    assert result["amount"].tolist() == [1500.0, 45000.0]
    assert result["year"].tolist() == [2024, 2024]
    assert result["month_name"].tolist() == ["January", "January"]
    assert result["amount_band"].tolist() == ["Medium", "Very High"]


def test_engineer_transaction_features_handles_invalid_dates_safely():
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN-0001"],
            "date": ["invalid-date"],
            "description": ["Test"],
            "category": ["Food"],
            "amount": [1000.0],
            "transaction_type": ["Expense"],
            "payment_method": ["UPI"],
        }
    )

    result = engineer_transaction_features(df)

    assert result["date"].isna().sum() == 1
    assert result["year"].isna().sum() == 1
    assert result["month_number"].isna().sum() == 1
    assert result["amount_band"].iloc[0] == "Medium"
