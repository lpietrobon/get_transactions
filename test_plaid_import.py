import plaid
from src.fetch_data import create_plaid_client  # Import the client creation function

try:
    client = create_plaid_client()  # Use the new client creation function
    print("Plaid library and PlaidApi client created successfully!")
except Exception as e:
    print(f"Error creating PlaidApi client: {e}")
