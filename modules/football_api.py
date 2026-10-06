from datetime import date

import requests
from flask import current_app


BASE_URL = "https://v3.football.api-sports.io"


def get_finished_matches(match_date=None):
    """
    Recupera tutte le partite concluse nella data indicata.

    Se match_date non viene specificata, utilizza la data odierna.
    """

    if match_date is None:
        match_date = date.today().isoformat()

    api_key = current_app.config["API_KEY"]

    if not api_key:
        raise RuntimeError("API_KEY non è configurata.")

    headers = {
        "x-apisports-key": api_key
    }

    params = {
        "date": match_date,
        "status": "FT-AET-PEN",
        "timezone": "Europe/Zurich"
    }

    response = requests.get(
        f"{BASE_URL}/fixtures",
        headers=headers,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if data.get("errors"):
        raise RuntimeError(
            f"Errore API-Football: {data['errors']}"
        )

    return data.get("response", [])