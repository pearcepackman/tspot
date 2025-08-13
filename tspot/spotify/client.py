from __future__ import annotations
import httpx
from typing import Any, Dict, Optional

from. auth import ensure_access_token

API_BASE = "https://api.spotify.com/v1"

class SpotifyClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self._session = httpx.Client(timeout = 10)

    def _headers(self) -> Dict[str, str]:
        token = ensure_access_token(self.client_id)
        return {"Authorization": f"Bearer {token}"}

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        resp = self._session.get(f"{API_BASE}{path}", headers=self._headers(), params=params)
        if resp.status_code == 401:
