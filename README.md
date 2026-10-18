# Expense Tracker App

A Python-based Expense Tracker application built with Streamlit that helps users explore income, expenses, savings, spending patterns, and monthly budget status through interactive data analytics and visualizations.

## Project Overview

Managing personal expenses is an important part of financial planning. This project demonstrates how Python and data analytics can be used to organize transaction data, identify spending patterns, monitor budgets, and generate meaningful financial insights.

The application uses synthetic transaction data and supports structured transaction storage with SQLite.

## Features

- **Expense and Income Tracking** — Organize transactions by category and transaction type.
- **Data Cleaning** — Validate transaction records and prepare clean data for analysis.
- **Exploratory Data Analysis (EDA)** — Analyze spending distributions and monthly financial trends.
- **Interactive Dashboard** — Explore key financial metrics and visualizations using Streamlit.
- **Budget Monitoring** — Classify spending as Normal, Near Limit, or Over Budget.
- **Monthly Budget Analysis** — Compare expenses against the selected month's budget.
- **Financial Insights** — Identify high-spending categories and changes in spending patterns.
- **Feature Engineering** — Derive useful features such as month, day of week, weekend status, and amount bands.
- **SQLite Storage** — Store and retrieve transactions using a local database.
- **Automated Tests** — Validate data processing, budget logic, and storage functionality.

## Technology Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit
- SQLite
- Pytest
- Git and GitHub

## Project Structure

```text
Expense Tracker App/
├── app.py
├── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── outputs/
├── src/
│   ├── generate_data.py
│   ├── data_cleaning.py
│   ├── analysis.py
│   ├── visualizations.py
│   ├── feature_engineering.py
│   ├── insights.py
│   └── storage.py
├── tests/
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/vinotha2007-V/Expense--Tracker--App.git
cd Expense--Tracker--App
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

### 3. Activate the environment

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Run Tests

Execute the automated tests with:

```bash
python -m pytest -q
```

## Data and Privacy

This project is designed for learning and portfolio demonstration using synthetic transaction data. It does not connect to real bank accounts or financial institutions. The SQLite database is stored locally and is excluded from Git tracking.

The example amounts and generated insights are for demonstration purposes only; they do not represent actual personal financial records or financial advice.

## Key Learning Outcomes

- Data cleaning and validation with Pandas
- Exploratory data analysis and data visualization
- Feature engineering for transaction data
- Budget threshold calculations and month-specific analysis
- SQLite database operations using Python
- Building interactive dashboards with Streamlit
- Writing automated tests with Pytest
- Organizing a Python project for GitHub

## Future Improvements

- Add manual transaction entry and editing through the dashboard
- Support configurable monthly budgets
- Export filtered transactions and summaries to CSV
- Improve dashboard filtering and reporting
- Add more automated tests and user documentation

## Author

**Vinotha**

GitHub: [vinotha2007-V](https://github.com/vinotha2007-V)

---

*Built as a portfolio project to practice Python, data analytics, visualization, and application development.*
