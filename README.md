## Status
- fetch_data.py runs with `python -m src.fetch_data`

Known mistakes
- SANDBOX_ACCESS_TOKEN is wrong. we need to actually exchange one


## structure
project_root/
├── src/
│   ├── main.py             (Data fetching and CSV export - main app)
│   ├── fetch_data.py       (Plaid API data fetching functions)
│   └── get_access_token.py (Script to obtain and store access tokens - one-time setup)
├── config.py
└── .env


get_access_token.py (One-Time Setup):

1. This script will handle the Plaid Link flow (primarily the backend part).
1. You'll run this once per financial institution account you want to connect.
1. It will guide you through the Plaid Link process (using the command line and potentially opening a browser window for the Plaid Link UI).
1. Upon successful linking, it will securely store the obtained access_token (e.g., in an encrypted file or system keychain).

main.py (Regular Data Fetching and Export):

1. This script will be your main application for daily/regular use.
1. It will:
    1. Read the securely stored access_token(s).
    1. Use fetch_data.py to fetch transactions for your linked accounts.
    1. Process and combine the data.
    1. Export everything to a CSV file.


Key points in get_access_token.py:

1. Plaid Link Backend Flow: This script uses the Plaid Link API's backend flow to create a link_token and then constructs the Plaid Link URL to open in a browser.
1. Simple HTTP Server: It includes a very basic Python HTTP server (StoringHTTPServer and LinkTokenCallbackHandler). This server listens for the Plaid Link callback after you successfully link an account in the browser.
1. Callback Handling: When Plaid Link redirects back to http://localhost:8080/callback with a public_token, the LinkTokenCallbackHandler captures the public_token.
1. Token Exchange: The exchange_public_token_for_access_token function exchanges the public_token for a permanent access_token.
1. Secure Storage Placeholder: The store_access_token_securely function is a placeholder. In a real application, you would replace this with a robust and secure way to store the access_token. For this simplified example, it just prints the access_token to the console (which is INSECURE for real use).

How to Run get_access_token.py:

1. Navigate to your project root in the terminal: cd project_root
1. Run the script: python -m src.get_access_token
1. Plaid Link Opens in Browser: The script will print a message and open Plaid Link in your default web browser.
1. Simulate Account Linking: Follow the Plaid Link UI to simulate linking a bank account using Plaid's test institutions and test credentials.
1. Callback and Access Token: After successful linking, the browser window will show a "Success" message, and the access_token will be printed in your terminal. Copy this access_token and store it securely.

## TODO:
- install flask

- Sandbox Access Token Purpose: The SANDBOX_ACCESS_TOKEN you were (and likely still are) using in fetch_data.py is not a generic, universally valid token. It's a placeholder that Plaid provides for testing purposes in the Sandbox environment. It simulates having an access token for a linked account, but it's not tied to any real or simulated bank account you have linked.

- Need to Link an Account (Even in Sandbox): To actually fetch realistic transaction data (even in the Sandbox), you need to go through a process of simulating linking a financial institution account using Plaid Link (or a similar flow) in the Sandbox environment. This process will result in a public_token, which you then exchange for a real (but sandbox-environment-specific) access_token that is associated with a simulated bank account.


Next Steps to Get a Valid Sandbox Access Token: Implement Plaid Link (Sandbox Mode):

- Simplest Approach (Quickest for testing): For basic testing in the Sandbox, you can use Plaid's pre-built Plaid Link UI (front-end component). You would embed this UI in a simple HTML page or potentially integrate it into a basic Python web framework (like Flask or a simple command-line interaction).


Plaid Link Flow in Sandbox (Simplified Steps):

- Initialize Plaid Link: You'll need to use JavaScript to initialize the Plaid Link UI in your HTML page (or however you are embedding it). You'll need to provide your public_key (Sandbox Public Key from Plaid Dashboard), client_name, env: 'sandbox', products: ['transactions'] (at least for transaction fetching), and a callback function to handle the onSuccess event when a user successfully links an account.

- Simulate Account Linking: When you run Plaid Link in the Sandbox, it will present a UI where you can select a test financial institution (provided by Plaid in the Sandbox). You will then use test credentials (also provided by Plaid in their Sandbox documentation) to simulate a successful login and account linking.
- public_token in onSuccess Callback: Upon successful simulated linking, Plaid Link's onSuccess callback function will receive a public_token. This public_token is temporary.
- Exchange public_token for access_token (Server-Side): You need to send this public_token to your Python backend (your fetch_data.py or a related script). In your Python code, you will use the Plaid API endpoint /item/public_token/exchange to exchange the public_token for a permanent access_token. This exchange must be done securely on your backend (not directly in client-side JavaScript).
- Store access_token (Securely): Once you get the access_token, you would typically store it securely (in a database, encrypted file, etc.) associated with the user/account. For this local testing app, you could simply print it to the console temporarily or store it in a variable in your Python script for immediate use.
- Use the access_token to Fetch Transactions: Now, you can use this newly obtained access_token in your fetch_transactions_plaid function to fetch transaction data for the simulated bank account you just linked.
