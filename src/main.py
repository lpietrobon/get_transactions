import argparse  # Optional for CLI

# from process_data import process_transaction_data
# from export_csv import export_dataframe_to_csv
import datetime

from config import API_PROVIDER, OUTPUT_CSV_FILE
from fetch_data import fetch_transactions


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and export financial transactions to CSV."
    )  # Optional CLI arguments
    parser.add_argument(
        "--start_date",
        help="Start date for transactions (YYYY-MM-DD)",
        default="2023-01-01",
    )  # Example argument
    parser.add_argument(
        "--end_date",
        help="End date for transactions (YYYY-MM-DD)",
        default=datetime.date.today().strftime("%Y-%m-%d"),
    )  # Example argument
    parser.add_argument(
        "--output_file", help="Output CSV file path", default=OUTPUT_CSV_FILE
    )  # Example argument
    args = parser.parse_args()

    # **Important:** In a real application, you would need to handle the initial
    # institution connection and obtain an `access_token` from the API provider.
    # This usually involves an OAuth flow or similar.  For testing, you might
    # use a test access token provided by the API provider.
    example_access_token = "your_test_access_token"  # Replace with a real access token

    try:
        raw_transactions = fetch_transactions(
            API_PROVIDER, example_access_token, args.start_date, args.end_date
        )
        # processed_dataframe = process_transaction_data(raw_transactions)
        # if not processed_dataframe.empty:
        #     export_dataframe_to_csv(processed_dataframe, args.output_file)
        # else:
        #     print("No transactions fetched or processed.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
