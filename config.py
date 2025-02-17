import os

from dotenv import load_dotenv

load_dotenv()

API_PROVIDER = "plaid"
OUTPUT_CSV_FILE = "transactions.csv"

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_ENVIRONMENT = os.getenv("PLAID_ENVIRONMENT", "sandbox")  # Default to sandbox
PLAID_SECRET = os.getenv("PLAID_SECRET")
SANDBOX_ACCESS_TOKEN = os.getenv("SANDBOX_ACCESS_TOKEN")
