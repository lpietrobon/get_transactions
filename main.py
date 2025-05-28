#!/usr/bin/env python
"""
main.py
▪ --add-account    ▸ open Plaid Link in browser, save new access-token
▪ --aggregate      ▸ pull accounts / balances / transactions → CSV
"""
from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

import os
import sys
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

import pandas as pd

import plaid
from crypto_store import (  # ← our tiny encrypted key-value store
    load_tokens,
    save_tokens,
)
from flask import Flask, request
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


# ────────────────────────────────────────────────────────────────────────────────
#  Configuration
# ────────────────────────────────────────────────────────────────────────────────

env_map = {
    "sandbox": plaid.Environment.Sandbox,
    "production": plaid.Environment.Production,
}
env = env_map.get(os.getenv("PLAID_ENV", "sandbox").lower())
if env is None:
    sys.exit("PLAID_ENV must be 'sandbox' or 'production'")

configuration = plaid.Configuration(
    host=env,
    api_key={
        "clientId": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
    },
)
client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

app = Flask(__name__)  # Flask is only used during add-account


# ────────────────────────────────────────────────────────────────────────────────
#  Helpers
# ────────────────────────────────────────────────────────────────────────────────
def get_start_date() -> date:
    """Return next date after last stored transaction, else 90 days ago."""
    csv_path = DATA_DIR / "transactions.csv"
    if not csv_path.exists():
        return (datetime.now() - timedelta(days=90)).date()

    try:
        # read last line only (fast even for large files)
        *_, last = csv_path.read_text().splitlines()
        last_date = pd.to_datetime(last.split(",")[0]).date()
        return last_date + timedelta(days=1)
    except Exception:
        return (datetime.now() - timedelta(days=90)).date()


@retry(
    retry=retry_if_exception_type(plaid.ApiException),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    stop=stop_after_attempt(3),
)
def get_transactions_page(access_token: str, start, end, count: int, offset: int = 0):
    """Fetch one page of transactions (retries on 5xx / 429)."""
    return client.transactions_get(
        TransactionsGetRequest(
            access_token=access_token,
            start_date=start,
            end_date=end,
            options=TransactionsGetRequestOptions(count=count, offset=offset),
        )
    )


# ────────────────────────────────────────────────────────────────────────────────
#  Link-token callback
# ────────────────────────────────────────────────────────────────────────────────
@app.route("/oauth-response")
def oauth_response():
    public_token = request.args.get("public_token")
    exch = client.item_public_token_exchange(
        ItemPublicTokenExchangeRequest(public_token=public_token)
    )

    # Institution name (best-effort, non-fatal if it fails)
    try:
        inst = client.institutions_get_by_id(
            InstitutionsGetByIdRequest(
                institution_id=exch.item_id,
                country_codes=[CountryCode("US")],
            )
        ).institution.name
    except plaid.ApiException:
        inst = "unknown"

    # ── merge & save tokens ────────────────────────────────────────────
    tokens = load_tokens()
    tokens.update(
        {
            exch.item_id: {
                "access_token": exch.access_token,
                "institution_name": inst,
            }
        }
    )
    save_tokens(tokens)
    # ------------------------------------------------------------------

    shutdown = request.environ.get("werkzeug.server.shutdown")
    if shutdown:
        shutdown()
    return "✅ Account linked. You can close this tab."

@app.route("/")
def index():
    # create a new link_token for *each* visit
    link_token = client.link_token_create(
        LinkTokenCreateRequest(
            user={"client_user_id": "user-1"},
            client_name="Personal Finance Manager",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
    ).link_token

    # “minimal viable” HTML that embeds the JS SDK
    return f"""
<!doctype html>
<html>
  <head>
    <title>Link your bank</title>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
  </head>
  <body style="font-family:sans-serif">
    <button id='link-btn'>Connect a bank account</button>
    <script>
      const handler = Plaid.create({{
        token: '{link_token}',
        onSuccess: (public_token, meta) =>
          window.location = '/oauth-response?public_token=' + public_token
      }});
      document.getElementById('link-btn').onclick = () => handler.open();
    </script>
  </body>
</html>"""



# ────────────────────────────────────────────────────────────────────────────────
#  Commands
# ────────────────────────────────────────────────────────────────────────────────
def add_account():
    from threading import Thread
    # 💡 use a port that is almost never taken, and bind to all interfaces
    server = Thread(
        target=lambda: app.run(host="0.0.0.0", port=8000, threaded=True, debug=False)
    )
    server.daemon = True
    server.start()

    # open the new endpoint
    webbrowser.open("http://127.0.0.1:8000")
    print("Complete the Plaid flow, then return here…")
    server.join()


def aggregate_data() -> None:
    tokens = load_tokens()
    if not tokens:
        print("No accounts linked. Run with --add-account first.")
        return

    all_tx, all_acct, all_bal = [], [], []
    start, end = get_start_date(), datetime.now().date()
    PAGE = 500

    for item_id, meta in tokens.items():
        access_token, inst = meta["access_token"], meta["institution_name"]

        # ── accounts & balances ────────────────────────────────────────
        acct_resp = client.accounts_get(AccountsGetRequest(access_token=access_token))
        for acct in acct_resp.accounts:
            a = acct.to_dict()
            a.update({"item_id": item_id, "institution_name": inst})
            all_acct.append(a)
            all_bal.append(
                {
                    "item_id": item_id,
                    "institution_name": inst,
                    "account_id": acct.account_id,
                    "current": acct.balances.current,
                    "available": acct.balances.available,
                    "iso_currency_code": acct.balances.iso_currency_code,
                }
            )

        # ── paginated transactions ────────────────────────────────────
        offset = 0
        while True:
            page = get_transactions_page(access_token, start, end, PAGE, offset)
            txns = page.transactions
            for t in txns:
                d = t.to_dict()
                d.update({"item_id": item_id, "institution_name": inst})
                all_tx.append(d)

            if len(txns) < PAGE:
                break
            offset += len(txns)

    # ── persist ────────────────────────────────────────────────────────
    pd.DataFrame(all_tx).to_csv(DATA_DIR / "transactions.csv", index=False)
    pd.DataFrame(all_acct).to_csv(DATA_DIR / "accounts.csv", index=False)
    pd.DataFrame(all_bal).to_csv(DATA_DIR / "balances.csv", index=False)

    print(f"✔ Pulled data {start}–{end} for {len(tokens)} item(s). See data/*.csv")


# ────────────────────────────────────────────────────────────────────────────────
#  CLI entry
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("--add-account", "--aggregate"):
        sys.exit("Usage: python main.py [--add-account | --aggregate]")

    {"--add-account": add_account, "--aggregate": aggregate_data}[sys.argv[1]]()
