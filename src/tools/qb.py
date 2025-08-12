import os
from typing import Any, Mapping

from dotenv import load_dotenv
from qbittorrent import Client  # type: ignore[import]

load_dotenv()

QBIT_URL = os.getenv("QBIT_URL", "")
QBIT_USER = os.getenv("QBIT_USER", "")
QBIT_PASSWORD = os.getenv("QBIT_PASSWORD", "")


def get_qb_client() -> Client:
    client = Client(QBIT_URL)
    client.login(QBIT_USER, QBIT_PASSWORD)
    return client


def qb_get_prefs(qb: Client) -> dict[str, Any]:
    raw = qb.preferences()

    assert isinstance(raw, Mapping), f"Unexpected type for preferences: {type(raw)}"

    return dict(raw)
