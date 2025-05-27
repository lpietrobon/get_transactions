import http.server
import socketserver
import webbrowser  # To open Plaid Link in a browser
from typing import cast, Optional

import plaid
from config import DUMMY_USER_ID, PLAID_CLIENT_ID, PLAID_ENVIRONMENT, PLAID_SECRET

from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products


def create_plaid_client():
    """Creates a Plaid API client using the configuration."""
    print(f"PLAID_ENVIRONMENT: '{PLAID_ENVIRONMENT}'")  # Debug print
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


client = create_plaid_client()


class StoringHTTPServer(socketserver.TCPServer):  # Custom server to store public_token
    public_token: Optional[str] = None


# --- Simple HTTP Server to Handle Plaid Link Redirect ---
class LinkTokenCallbackHandler(http.server.SimpleHTTPRequestHandler):
    server: socketserver.BaseServer

    def do_GET(self):
        if self.path.startswith("/callback") and "public_token" in self.path:
            query_components = dict(
                qc.split("=") for qc in self.path.split("?")[1].split("&")
            )
            public_token = query_components.get("public_token")
            if public_token:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                response_html = f"""
                <html>
                <head><title>Plaid Link Success</title></head>
                <body>
                    <h1>Plaid Account Linked Successfully!</h1>
                    <p>Public Token: <strong>{public_token}</strong></p>
                    <p>You can close this browser window now and return to your terminal.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
                self.wfile.write(response_html.encode())
                cast(StoringHTTPServer, self.server).public_token = public_token
            else:
                self.send_error(
                    400, "Bad Request", "Public token not found in callback URL"
                )
        else:
            self.send_error(404)


# --- Get Link Token and Launch Plaid Link ---
def get_link_token():
    try:
        user = LinkTokenCreateRequestUser(client_user_id=DUMMY_USER_ID)
        request = LinkTokenCreateRequest(
            client_name="My Local Finance App",
            user=user,
            products=[Products("transactions")],  # Request transaction data access
            country_codes=[CountryCode("US")],  # Or your country codes
            language="en",
            redirect_uri="http://localhost:8080/callback",  # Important: Must match Plaid Dashboard settings (if used)
            # environment=PLAID_ENVIRONMENT,
        )
        link_token_response = client.link_token_create(request)
        return link_token_response["link_token"]
    except ApiException as e:
        print(f"Error creating Link Token: {e}")
        return None


def exchange_public_token_for_access_token(public_token):
    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response["access_token"]
        item_id = exchange_response["item_id"]
        print(
            f"Successfully exchanged public token for access token. Item ID: {item_id}"
        )
        return access_token, item_id  # Return item_id as well
    except ApiException as e:
        print(f"Error exchanging public token: {e}")
        return None, None


def store_access_token_securely(
    access_token, item_id, account_identifier
):  # Added account_identifier
    """
    Placeholder for secure storage of access_token and item_id.
    Also takes account_identifier to name the token.
    In a real app, use a secure method like keyring, encrypted file, or database.
    """
    # TODO: Replace the printing with a secure storage method
    print(
        f"\n**IMPORTANT: Access Token and Item ID Obtained for '{account_identifier}':**"
    )  # Include identifier in message
    print(f"Account Identifier: {account_identifier}")  # Print identifier
    print(f"Access Token: {access_token}")
    print(f"Item ID: {item_id}")
    print(
        f"**You should store these securely, associated with '{account_identifier}' (e.g., in a password manager or encrypted file).**"
    )
    # In a real application, you would use a secure storage mechanism here,
    # likely using the account_identifier as part of the storage key.


if __name__ == "__main__":
    account_identifier = input(
        "Enter an identifier for this financial institution account (e.g., BankOfAmerica, CreditCard1): "
    )
    if not account_identifier:
        print("Account identifier cannot be empty. Exiting.")
        exit()

    link_token = get_link_token()
    if not link_token:
        print("Failed to get Link Token. Exiting.")
        exit()

    link_url = f"https://link.plaid.com/?token={link_token}&redirect_uri=http://localhost:8080/callback"
    print(f"Opening Plaid Link for '{account_identifier}' in your browser: {link_url}")
    webbrowser.open(link_url)

    # --- Start a simple HTTP server to listen for the Plaid Link callback ---
    PORT = 8080
    with StoringHTTPServer(("", PORT), LinkTokenCallbackHandler) as httpd:
        print(
            f"Serving at port {PORT}. Waiting for Plaid Link callback for '{account_identifier}'..."
        )  # Include identifier in message
        httpd.timeout = 120  # Timeout after 2 minutes if no callback received
        while httpd.public_token is None:  # Keep serving until public_token is received
            httpd.handle_request()  # Handle one request at a time (blocking)

        public_token = httpd.public_token
        print(
            f"\nPublic Token received from Plaid Link callback for '{account_identifier}':",
            public_token,
        )

        access_token, item_id = exchange_public_token_for_access_token(public_token)
        if access_token:
            store_access_token_securely(access_token, item_id, account_identifier)
        else:
            print("Failed to exchange public token for access token.")
