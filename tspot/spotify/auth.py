from __future__ import annotations
import json
import os
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

from spotipy.oauth2 import SpotifyPKCE
import time

#Defining where are tokens are going and the scopes of them
APP_DIR = Path.home() / ".tspot"
TOKENS_PATH = APP_DIR / "tokens.json"
SCOPES = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-modify-private"

@dataclass
#TokenSet keeps all of these tokens together for later usage
class TokenSet:
    access_token: str
    refresh_token: Optional[str]
    expires_at: int

# Ensures there's a directory for these toekns to go
def _ensure_app_dir():
    APP_DIR.mkdir(parents = True, exist_ok = True)
    try:
        #Limits access to user permissions only
        os.chmod(APP_DIR, 0o700)
    except Exception:
        pass

# Saving tokens to that previously mentioned token file
def save_tokens(tokens : TokenSet):
    #Ensuring the app directory works first
    _ensure_app_dir()
    # Building JSON data with the tokens I got
    data = {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "expires_at": tokens.expires_at,
    }
    # Dump JSON data to that file
    TOKENS_PATH.write_text(json.dumps(data, indent = 2))
    try:
        #0o600 is the user, so limits access to user only
        os.chmod(TOKENS_PATH, 0o600)
    except Exception:
        pass

# load_tokens either returns a TokenSet or None
def load_tokens() -> Optional[TokenSet]:
    if not TOKENS_PATH.exists():
        return None
    # If the tokens are present in the TOKENS_PATH, read it
    data = json.loads(TOKENS_PATH.read_text())
    return TokenSet(
        access_token = data["access_token"],
        refresh_token = data.get("refresh_token"),
        expires_at = int(data["expires_at"]),
    )

# Sets expiry time to 30 seconds
def is_expired(tokens : TokenSet) -> bool:
    return time.time() > (tokens.expires_at - 30)

def get_pkce_manager(client_id: str, redirect_uri: str = "http://localhost:8888/callback") -> SpotifyPKCE:
    return SpotifyPKCE(
        client_id = client_id,
        redirect_uri = redirect_uri,
        scope = SCOPES,
    )

# Handles any and all Callbacks, basically the only valid link is the one I set up above
class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL, if anything other than callback, 404 user
        parsed = urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404); self.end_headers(); return
        # Parse the query with this link and get the code 
        qs = parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
        # No code? 400 to user
        if not code:
            self.send_response(400); self.end_headers(); return

        # Stash code on the server and signal the event
        self.server.auth_code = code               
        self.server.auth_event.set()                 

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><body>Login complete. You can close this tab.</body></html>")

# Waiting for code on port 8888
def wait_for_code(port: int = 8888, timeout: float = 120.0) -> str:
    # Server sticks on port 8888, uses _CallbackHandler to verify the right port
    httpd = HTTPServer(("127.0.0.1", port), _CallbackHandler)

    # Attach an event object to the server instead of waiting
    httpd.auth_event = threading.Event()           
    httpd.auth_code = None                         

    # Serve requests in a background thread
    t = threading.Thread(target=httpd.handle_request, daemon=True)
    t.start()

    # Wait until handler signals or timeout
    if not httpd.auth_event.wait(timeout=timeout):
        raise TimeoutError("OAuth callback not received in time.")

    code = httpd.auth_code                    
    if not code:
        raise RuntimeError("No authorization code received.")
    return code

# Login will be returning TokenSet for parsing
def login(client_id: str) -> TokenSet:
    _ensure_app_dir()
    auth = get_pkce_manager(client_id)
    url = auth.get_authorize_url()
    
    #Open user's browser
    import webbrowser
    webbrowser.open(url, new = 1, autoraise=True)
    #Waiting for redirect, then capture the code
    code = _wait_for_code(8888)
    token_info = auth.get_access_token(code, as_dict=True)
    tokens = TokenSet (
        access_token = token_info["access_token"],
        refresh_token = token_info.get("refresh_token"),
        expires_at = int(token_info["expires_at"]),
    )
    save_tokens(tokens)
    return tokens

def ensure_access_token(client_id: str) -> str:
    """Load existing tokens or login; refresh if needed; return valid access token."""
    tokens = load_tokens()
    if tokens is None:
        tokens = login(client_id)
        return tokens.access_token
    if is_expired(tokens):
        auth = get_pkce_manager(client_id)
        # PKCE exchanges code for access token; refresh token support can be limited in PKCE.
        # If no refresh_token is present, fallback to re-login.
        if tokens.refresh_token:
            # spotipy PKCE class may not expose a direct refresh; re-login is simplest/reliable:
            tokens = login(client_id)
        else:
            tokens = login(client_id)
        return tokens.access_token
    return tokens.access_token