import base64
import os
import urllib.parse
import urllib.request
from flask import flask

CLIENT_ID = "6f9aef3c3b57437a96b22a65bd487cd6"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "user-read-playback-state"

def main():
    print("TESTING")
    verifier, challenge = make_verifier_and_challenge()
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "code_challenge": challenge,
        "code_challenge_method": 'S256',
        "response_type": "code"
    }
    print(params)
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    print(auth_url)
    request_handler()



    

def make_verifier_and_challenge():
    verifier = os.urandom(10)
    challenge = base64.urlsafe_b64encode(verifier)
    print("TEST")
    print(verifier)
    print(challenge)
    return verifier, challenge

def request_handler():
    app = flask(__name__)
    @app.route("/hello")




main()