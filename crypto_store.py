# crypto_store.py
import base64, json, os, struct
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

DATA_DIR = Path("data")
TOK_FILE = DATA_DIR / "tokens.bin"
TOK_FILE.parent.mkdir(exist_ok=True)

# 1️⃣ master key from env
try:
    _raw = base64.urlsafe_b64decode(os.environ["ENC_KEY"])
    if len(_raw) != 32:
        raise ValueError
except (KeyError, ValueError):
    raise RuntimeError("Set a valid 32-byte base64 ENC_KEY env-var/.env")

fernet = Fernet(base64.urlsafe_b64encode(_raw))


def _wrap(plain: bytes) -> bytes:
    salt = os.urandom(16)  # travels with the blob
    token = fernet.encrypt(plain)
    return struct.pack(">I", len(salt)) + salt + token


def _unwrap(blob: bytes) -> bytes:
    n = struct.unpack(">I", blob[:4])[0]
    token = blob[4 + n :]
    try:
        return fernet.decrypt(token)
    except InvalidToken:
        raise RuntimeError("🔒  Wrong ENC_KEY or corrupt token file – relink accounts")


def load_tokens() -> dict:
    if not TOK_FILE.exists():
        return {}
    return json.loads(_unwrap(TOK_FILE.read_bytes()))


def save_tokens(tokens: dict) -> None:
    TOK_FILE.write_bytes(_wrap(json.dumps(tokens).encode()))
