import os

from dotenv import load_dotenv

load_dotenv(
    override=True
)  # Set override=True to overwrite existing OS environment variables

API_PROVIDER = "plaid"
OUTPUT_CSV_FILE = "transactions.csv"
BANK_IDENTIFIERS = ["BANK_A", "BANK_B"]  # Define your bank identifiers here

# PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
# PLAID_ENVIRONMENT = os.getenv("PLAID_ENVIRONMENT", "sandbox")  # Default to sandbox
# PLAID_SECRET = os.getenv("PLAID_SECRET")
# SANDBOX_ACCESS_TOKEN = os.getenv("SANDBOX_ACCESS_TOKEN")


# DUMMY_USER_ID = "my_dummy_uid"
