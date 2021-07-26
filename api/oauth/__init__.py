"""This resource provides endpoints for generating random state and nonce parametrs for 
porpuse of Google's OpenID Connect. It also gets JWT token for user and stores it in user profile.
For fouther reference read code."""

import api.oauth.service as service
from api.common.rest import post, ResourceEndpoint
from typing import List

endpoints: List[ResourceEndpoint] = [
    post('/oauth/state', service.generate_state_and_nonce),
    post('/oauth/state/verify', service.verify_state),
]