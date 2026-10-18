"""Safe data cleaning utilities for the expense tracker project.

These functions validate required columns, normalize transaction labels, remove
invalid or duplicate records, and save a cleaned CSV without silently discarding
problematic input without reporting it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

REQUIRED_COLUMNS = {
    "transaction_id",
    "date",
    "description",
    "category",
    "amount",
    "transaction_type",
    "payment_method",
}

VALID_TRANSACTION_TYPES = {"Expense", "Income"}
VALID_EXPENSE_CATEGORIES = {
    "Food",
    "Transport",
    "Rent",
    "Shopping",
    "Healthcare",
    "Education",
    "Utilities",
    "Entertainment",
    "Other",
}


def validate_required_columns(df: pd.DataFrame) -> None:
    """Raise a clear error if key columns are missing."""
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")


def normalize_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize type and category labels while preserving data integrity."""
    result = df.copy()
    result["transaction_type"] = (
        result["transaction_type"].astype(str).str.strip().str.title()
    )
    result["category"] = result["category"].astype(str).str.strip().str.title()
    result["payment_method"] = result["payment_method"].astype(str).str.strip().str.title()
    result["description"] = result["description"].fillna("Unknown transaction").astype(str).str.strip()
    return result


def clean_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Validate, normalize, and filter invalid records, returning a summary report."""
    validate_required_columns(df)
    cleaned = normalize_labels(df)

    report: Dict[str, int] = {
        "rows_before": len(cleaned),
        "missing_values": int(cleaned.isna().sum().sum()),
        "duplicate_ids_removed": 0,
        "invalid_dates_removed": 0,
        "invalid_amounts_removed": 0,
        "invalid_transaction_types_removed": 0,
        "category_mismatches_corrected": 0,
        "rows_after": 0,
    }

    cleaned["transaction_id"] = cleaned["transaction_id"].astype(str).str.strip()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    report["invalid_dates_removed"] = int(cleaned["date"].isna().sum())
    cleaned = cleaned[cleaned["date"].notna()].copy()

    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    report["invalid_amounts_removed"] = int(cleaned["amount"].isna().sum() + (cleaned["amount"] <= 0).sum())
    cleaned = cleaned[cleaned["amount"].notna() & (cleaned["amount"] > 0)].copy()

    cleaned = cleaned.drop_duplicates(subset=["transaction_id"], keep="first")
    report["duplicate_ids_removed"] = int(len(df) - len(cleaned))

    valid_type_mask = cleaned["transaction_type"].isin(VALID_TRANSACTION_TYPES)
    invalid_type_count = int((~valid_type_mask).sum())
    report["invalid_transaction_types_removed"] = invalid_type_count
    cleaned = cleaned[valid_type_mask].copy()

    cleaned.loc[cleaned["transaction_type"] == "Income", "category"] = "Salary"

    income_mismatch_mask = (cleaned["transaction_type"] == "Expense") & (
        cleaned["category"] == "Salary"
    )
    if income_mismatch_mask.any():
        report["category_mismatches_corrected"] += int(income_mismatch_mask.sum())
        cleaned.loc[income_mismatch_mask, "category"] = "Other"

    expense_invalid_mask = (cleaned["transaction_type"] == "Expense") & (
        ~cleaned["category"].isin(VALID_EXPENSE_CATEGORIES)
    )
    if expense_invalid_mask.any():
        report["category_mismatches_corrected"] += int(expense_invalid_mask.sum())
        cleaned.loc[expense_invalid_mask, "category"] = "Other"

    cleaned["category"] = cleaned["category"].str.title()
    report["rows_after"] = len(cleaned)
    return cleaned, report


def main() -> None:
    """Load the raw CSV, clean it, and save the processed dataset."""
    input_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "expenses.csv"
    output_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "expenses_clean.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    raw_df = pd.read_csv(input_path)
    cleaned_df, report = clean_transactions(raw_df)
    cleaned_df.to_csv(output_path, index=False)

    print(f"Rows before cleaning: {report['rows_before']}")
    print(f"Rows after cleaning: {report['rows_after']}")
    print(f"Missing values: {report['missing_values']}")
    print(f"Duplicate IDs removed: {report['duplicate_ids_removed']}")
    print(f"Invalid dates removed: {report['invalid_dates_removed']}")
    print(f"Invalid amounts removed: {report['invalid_amounts_removed']}")
    print(f"Invalid transaction types removed: {report['invalid_transaction_types_removed']}")
    print(f"Category mismatches corrected: {report['category_mismatches_corrected']}")
    print(f"Cleaned data saved to: {output_path}")


if __name__ == "__main__":
    main()
