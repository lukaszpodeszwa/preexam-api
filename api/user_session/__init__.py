from typing import Tuple, List

from api.common.rest import ResourceEndpoint, delete, get, post
from api.user_session.service import login, logout, get_token

endpoints: List[ResourceEndpoint] = [
    post('/user_session', login),
    delete('/user_session', logout),
    get('/user_session', get_token)
]
