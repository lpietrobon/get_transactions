import datetime
import json
import os

from config import API_PROVIDER, BANK_IDENTIFIERS, OUTPUT_CSV_FILE

from src.api.app import create_app
from src.export_csv import export_dataframe_to_csv
from src.fetch_data import fetch_transactions
from src.process_data import process_transaction_data


def load_access_tokens_securely():
    """Loads a list of access tokens from environment variables."""
    access_tokens = []
    for bank_id in BANK_IDENTIFIERS:
        token = os.getenv(f"PLAID_ACCESS_TOKEN_{bank_id}")
        if token:
            access_tokens.append(token)
    return access_tokens


def main():
    access_tokens = load_access_tokens_securely()
    if not access_tokens:
        print(
            "Error: No access tokens found in environment variables (PLAID_ACCESS_TOKEN_BANK_A, PLAID_ACCESS_TOKEN_BANK_B, etc.)."
        )
        print(
            "Run get_access_token.py for each financial institution to obtain access tokens."
        )
        return

    all_transactions_data = []  # List to hold transactions from all banks

    start_date_str = "2023-01-01"
    end_date_str = datetime.date.today().strftime("%Y-%m-%d")

    for access_token in access_tokens:  # Iterate through each access token
        try:
            raw_transactions = fetch_transactions(
                API_PROVIDER, access_token, start_date_str, end_date_str
            )
            if raw_transactions:
                print(
                    f"Successfully fetched transactions for one account (first 5 for preview):"
                )
                print(json.dumps(raw_transactions["transactions"][:5], indent=2))
                all_transactions_data.extend(
                    raw_transactions["transactions"]
                )  # Add transactions to the combined list
            else:
                print("Failed to fetch transactions for one account.")
        except Exception as e:
            print(f"Error fetching transactions for one account: {e}")

    if all_transactions_data:
        print(
            f"\nTotal transactions fetched from all accounts: {len(all_transactions_data)}"
        )
        processed_dataframe = process_transaction_data(
            {"transactions": all_transactions_data}
        )  # Process combined data
        if not processed_dataframe.empty:
            export_dataframe_to_csv(processed_dataframe, OUTPUT_CSV_FILE)
        else:
            print("No transactions to export after processing.")
    else:
        print("No transactions fetched from any accounts.")


if __name__ == "__main__":
    # main()
    #  with the flask app
    app = create_app()
    app.run(debug=True)
