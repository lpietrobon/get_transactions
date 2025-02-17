import os

from dotenv import load_dotenv

load_dotenv()

API_PROVIDER = "plaid"
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENVIRONMENT = os.getenv("PLAID_ENVIRONMENT", "sandbox")  # Default to sandbox
OUTPUT_CSV_FILE = "transactions.csv"
