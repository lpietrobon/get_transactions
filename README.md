# 🏦 Personal Finance Aggregator (Plaid)

This is a command-line tool to:

- 🔐 Securely connect your financial accounts using [Plaid Link](https://plaid.com/docs/link/)
- 📥 Download account data, balances, and transactions
- 📊 Export to CSV for analysis or integration into other tools

Built for **local use**, with support for encrypted token storage and daily aggregation via script.

## TODO
	•	await until Plai's security questionnair is approved
	•	Add support for more Plaid products (e.g., assets, investments)
	•	Support refresh of expired tokens
	•	CI integration (e.g., GitHub Actions for scheduled pulls)
	•	Optional: GUI or notebook for viewing and analyzing the data


---

## 🚀 Features

- `--add-account`: Opens Plaid Link to securely add a financial institution
- `--aggregate`: Downloads and saves:
  - Accounts
  - Balances
  - Transactions (paginated)
- Persists data to CSV files in a local `data/` directory
- Retries on rate limiting or 5xx server errors using [tenacity](https://tenacity.readthedocs.io/)
- Flask-based temporary server for Plaid OAuth callback
- Lightweight encrypted token store (`crypto_store.py`)

---

## 🛠 Requirements

- Python 3.10+
- A [Plaid developer account](https://dashboard.plaid.com/signup)
- Sandbox credentials (or live credentials if moving to production)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Setup
	1.	Create a .env file in the root directory:
```
PLAID_ENV=sandbox
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_or_live_secret
```
    2.	Run with: `python main.py --add-account`. This will open your browser to the Plaid Link flow. Once linked, credentials are stored encrypted.

---

## Usage
```bash
# Link a new account
python main.py --add-account

# Pull latest balances & transactions
python main.py --aggregate
```
