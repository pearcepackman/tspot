# pkce_min.py
import base64, hashlib, os, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, time
import requests

CLIENT_ID = "<your_spotify_client_id>"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "user-read-playback-state user-modify-playback-state"

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def make_verifier_and_challenge():
    verifier = b64url(os.urandom(64))  # ~86 chars
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge

verifier, challenge = make_verifier_and_challenge()

params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPES,
    "code_challenge_method": "S256",
    "code_challenge": challenge,
}

auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

# --- tiny one-off HTTP server to capture ?code= ---
code_holder = {"code": None}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.urlparse(self.path)
        if q.path != "/callback":
            self.send_response(404); self.end_headers(); return
        qs = urllib.parse.parse_qs(q.query)
        code_holder["code"] = qs.get("code", [None])[0]
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Auth complete. You can close this window.")
    def log_message(self, *args, **kwargs): pass

httpd = HTTPServer(("localhost", 8888), Handler)
webbrowser.open(auth_url)
print("Opened browser for Spotify login...")

# poll the server until we get the code (single request)
while code_holder["code"] is None:
    httpd.handle_request()

auth_code = code_holder["code"]
print("Got code:", auth_code[:8], "...")

# --- token exchange ---
data = {
    "client_id": CLIENT_ID,
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "code_verifier": verifier,
}
token = requests.post("https://accounts.spotify.com/api/token", data=data).json()
print(json.dumps({k: token[k] for k in token if k != "access_token"}, indent=2))
access_token = token["access_token"]

# --- test the token ---
me = requests.get("https://api.spotify.com/v1/me",
                  headers={"Authorization": f"Bearer {access_token}"}).json()
print("Hello,", me.get("display_name") or me.get("id"))
