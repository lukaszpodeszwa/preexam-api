import base64
import hashlib
import json
import os
import random
import sys
from typing import Dict

import requests

import api.database
import api.oauth.schema as schema
import api.user_session.service
from api.common.service import ServiceRequest, ServiceResponse
from api.errors import ApiError, api_error
from api.middlewares import validate

# Stores states and their nonces.
states: Dict[str, str] = {}

try:
    OAUTH_GOOGLE_CLIENT_ID = os.environ['OAUTH_GOOGLE_CLIENT_ID']
    OAUTH_GOOGLE_CLIENT_SECRET = os.environ['OAUTH_GOOGLE_CLIENT_SECRET']
    OAUTH_GOOGLE_REDIRECT_URI = os.environ['OAUTH_GOOGLE_REDIRECT_URI']
except KeyError as e:
    sys.exit(f'Env var {e} is not set!')


def _decode_id_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        print('incorrect token format')
    payload = parts[1]
    padded = payload + '=' * (4 - len(payload) % 4)
    decoded = base64.b64decode(padded)
    return json.loads(decoded)


def generate_state_and_nonce(r: ServiceRequest) -> ServiceResponse:
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    nonce = hashlib.sha256(os.urandom(512)).hexdigest()
    states[state] = nonce
    return ServiceResponse(201, {'state': state, 'nonce': nonce})


@validate(schema.VALIDATE_STATE)
def verify_state(r: ServiceRequest) -> ServiceResponse:
    """Check if pair state:nonce is present in known states.
    If yes then get user data from Google and check if account exists.
    If yes then create api session otherwise add account and then create session."""

    nonce = states.get(r.content['state'])
    if not nonce or nonce != r.content['nonce']:
        return ServiceResponse(403, errors=api_error('invalid_state_or_nonce'))

    # Exchange one time code for id_token.
    req = requests.post('https://oauth2.googleapis.com/token',
                        json={
                            'code': r.content['code'],
                            'client_id': 'your-client-id&',
                            'client_secret': 'your-client-secret&',
                            'redirect_uri':
                            'https%3A//oauth2.example.com/code&',
                            'grant_type': 'authorization_code',
                        })

    id_token = _decode_id_token(req.json()['id_token'])

    existing_account = api.database.db.accounts.find_one(
        {'email': id_token['email']})

    if not existing_account:
        existing_account = {
            'email': id_token['email'],
            'username': id_token['name'],
            'name': id_token['given_name'],
            'last_name': id_token['family_name'],
            'role': 'user',
            'newsletter': True,
            'show_history': True,
        }
        api.database.insert_one('accounts', existing_account)

    token_data = {
        'role': existing_account['role'],
        'user_id': existing_account['_id'],
    }
    session_token = api.user_session.service._generate_session_token(
        token_data)
    api.database.insert_one('session_tokens', session_token)
    return ServiceResponse(201, {'session_token': session_token})
