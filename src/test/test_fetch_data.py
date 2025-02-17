import json
import unittest
from unittest.mock import MagicMock, patch

from fetch_data import fetch_transactions_plaid


class TestFetchData(unittest.TestCase):

    @patch("plaid.Client")  # Mock the plaid.Client class
    def test_fetch_transactions_plaid_success(self, MockPlaidClient):
        """Test successful transaction fetching from Plaid."""
        mock_client_instance = MockPlaidClient.return_value
        mock_client_instance.Transactions.get.return_value = (
            {  # Mock successful response
                "transactions": [
                    {
                        "transaction_id": "1",
                        "amount": 10.00,
                        "date": "2023-10-26",
                        "name": "Test Transaction 1",
                    },
                    {
                        "transaction_id": "2",
                        "amount": 25.50,
                        "date": "2023-10-25",
                        "name": "Test Transaction 2",
                    },
                ],
                "accounts": [],
                "item": {},
                "total_transactions": 2,
            }
        )

        access_token = "test_access_token"
        start_date = "2023-01-01"
        end_date = "2023-12-31"

        transactions_data = fetch_transactions_plaid(access_token, start_date, end_date)

        self.assertIsNotNone(transactions_data)
        self.assertIsInstance(transactions_data, dict)
        self.assertIn("transactions", transactions_data)
        self.assertEqual(len(transactions_data["transactions"]), 2)
        self.assertEqual(transactions_data["transactions"][0]["transaction_id"], "1")

    @patch("plaid.Client")
    def test_fetch_transactions_plaid_error(self, MockPlaidClient):
        """Test Plaid API error handling."""
        mock_client_instance = MockPlaidClient.return_value
        mock_client_instance.Transactions.get.side_effect = (
            plaid.exceptions.PlaidError(  # Mock an API error
                "INVALID_ACCESS_TOKEN",
                "INVALID_INPUT",
                "The access_token provided is invalid.",
                http_status_code=400,
            )
        )

        access_token = "invalid_access_token"
        start_date = "2023-01-01"
        end_date = "2023-12-31"

        transactions_data = fetch_transactions_plaid(access_token, start_date, end_date)

        self.assertIsNone(transactions_data)  # Expect None to be returned on error


if __name__ == "__main__":
    unittest.main()
