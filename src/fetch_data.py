import datetime

import plaid
from config import PLAID_CLIENT_ID, PLAID_ENVIRONMENT, PLAID_SECRET
from plaid.api import plaid_api
from plaid.exceptions import ApiException  # Correct import for exceptions
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions


def create_plaid_client():
    """Creates a Plaid API client using the configuration."""
    configuration = plaid.Configuration(
        host=getattr(plaid.Environment, PLAID_ENVIRONMENT.capitalize()),
        api_key={
            "clientId": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
        },
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    return client


def fetch_transactions_plaid(access_token, start_date, end_date):
    """
    Fetches transaction data from Plaid.

    Args:
        access_token (str): Plaid access token.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).

    Returns:
        dict: JSON response from Plaid API containing transactions, or None on error.
    """
    client = create_plaid_client()

    try:
        options = (
            TransactionsGetRequestOptions()
        )  # Instantiate request options if needed (check docs for options)
        request = TransactionsGetRequest(  # Use TransactionsGetRequest from plaid.model
            access_token=access_token,
            start_date=datetime.datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.datetime.strptime(end_date, "%Y-%m-%d").date(),
            options=options,  # Include options in the request
        )

        api_response = client.transactions_get(
            request
        )  # Call transactions_get on the client

        # Process and return the transaction data. The response structure is now more clearly defined.
        transactions_data = {
            "transactions": [
                txn.to_dict() for txn in api_response["transactions"]
            ],  # Convert each Transaction object to dict
            "accounts": [
                account.to_dict() for account in api_response["accounts"]
            ],  # Convert Account objects to dict
            "item": api_response["item"].to_dict(),  # Convert Item object to dict
            "total_transactions": api_response["total_transactions"],
        }
        return transactions_data

    except ApiException as e:  # Catch ApiException (from plaid.exceptions)
        print(f"Plaid API Error: {e}")
        print(f"HTTP Response Body: {e.body}")  # Print response body for debugging
        return None


def fetch_transactions(api_provider, access_token, start_date, end_date):
    if api_provider == "plaid":
        return fetch_transactions_plaid(access_token, start_date, end_date)
    else:
        raise ValueError(f"Unsupported API provider: {api_provider}")


if __name__ == "__main__":
    SANDBOX_ACCESS_TOKEN = "access-sandbox-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Replace with your sandbox access token
    start_date_str = "2023-01-01"
    end_date_str = datetime.date.today().strftime("%Y-%m-%d")

    if SANDBOX_ACCESS_TOKEN == "access-sandbox-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx":
        print(
            "WARNING: Please replace 'SANDBOX_ACCESS_TOKEN' in fetch_data.py with a valid Plaid Sandbox access token."
        )
    else:
        transactions_json = fetch_transactions(
            "plaid", SANDBOX_ACCESS_TOKEN, start_date_str, end_date_str
        )
        if transactions_json:
            import json

            print(json.dumps(transactions_json, indent=2))
        else:
            print("Failed to fetch transactions.")
