import plaid
from config import (  # Relative import for config
    PLAID_CLIENT_ID,
    PLAID_ENVIRONMENT,
    PLAID_SECRET,
)
from flask import Blueprint, jsonify, render_template, request
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser

api_bp = Blueprint("api", __name__)


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


client = create_plaid_client()


@api_bp.route("/")
def index():
    """Serves the index.html page with Plaid Link UI."""
    return render_template("index.html", plaid_public_key=PLAID_CLIENT_ID)


@api_bp.route("/get_link_token", methods=["POST"])
def get_link_token_route():
    """Creates a Link Token and returns it as JSON."""
    try:
        # Create Link Token request
        request = LinkTokenCreateRequest(
            client_name="My Local Finance App",
            user=LinkTokenCreateRequestUser(),
            products=["transactions"],  # Replace with desired products
            country_codes=["US"],  # Replace with desired country codes
            language="en",
            redirect_uri="http://localhost:5000/callback",  # Ensure this matches your Plaid Dashboard Redirect URI
            environment=PLAID_ENVIRONMENT,
        )
        link_token_response = client.link_token_create(request)
        link_token = link_token_response["link_token"]
        print(f"Link token created: {link_token}")  # Log the link_token on server side
        return jsonify({"link_token": link_token})  # Return link_token as JSON
    except ApiException as e:
        print(f"Error creating Link Token: {e}")
    return jsonify({"error": "Could not create link token"}), 500


@api_bp.route("/exchange_public_token", methods=["POST"])
def exchange_public_token():
    """Exchanges the public_token for an access_token."""
    data = request.get_json()  # Safely parse JSON from the request
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    public_token = data.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400
    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response["access_token"]
        item_id = exchange_response["item_id"]
        print(f"Access Token: {access_token}, Item ID: {item_id}")
        return jsonify({"access_token": access_token})
    except ApiException as e:
        print(f"Error exchanging public token: {e}")
        return jsonify({"error": "Failed to exchange public token"}), 500
