import hashlib
import random
from time import time
from typing import Dict, Union

import api.database
from api.common.other import UserSession
from api.common.service import ServiceRequest, ServiceResponse
from api.errors import ApiError, api_error
from api.middlewares import require_auth, validate
from api.user_session import schema
from argon2 import PasswordHasher, exceptions
from typing_extensions import TypedDict

ph = PasswordHasher()


def _generate_session_token(token_data: Dict):
    expire_time = int(time()) + 3 * 3600
    hash_string = str(time) + ''.join(
        [str(x) for x in random.sample(range(0, 9), 4)])
    session_token = hashlib.sha1(hash_string.encode()).hexdigest()
    token_data['token'] = session_token
    token_data['exp'] = expire_time
    return token_data


@validate(schema.LOGIN)
def login(r: ServiceRequest) -> ServiceResponse:
    email = r.content['email']
    password = r.content['password']
    user_account = api.database.db.accounts.find_one({'email': email})

    if not user_account:
        error = api_error('invalid_login_or_password')
        return ServiceResponse(401, errors=error)

    blocked_to = None
    try:
        blocked_to = user_account['blocked']['to']
    except KeyError:
        pass
    if (isinstance(blocked_to, int) and blocked_to > int(time())):
        return ServiceResponse(401, errors=api_error('account_blocked'))
    try:
        # Field password can not be present when account is created by using
        # Sign-In eith Google.
        ph.verify(user_account.get('password', ''), password)
    except exceptions.VerifyMismatchError:
        error = api_error('invalid_login_or_password')
        return ServiceResponse(401, errors=error)

    token_data = {
        'role': user_account['role'],
        'user_id': user_account['_id'],
    }
    session_token = _generate_session_token(token_data)
    api.database.insert_one('session_tokens', session_token)
    token = {'session_token': session_token['token']}
    return ServiceResponse(201, token)


@require_auth()
def logout(r: ServiceRequest) -> ServiceResponse:
    return api.database.delete_one('session_tokens', r.user_session._id)


@require_auth()
def get_token(r: ServiceRequest) -> ServiceResponse:
    return api.database.find_one('session_tokens',
                                 {'token': r.user_session.token}, {
                                     '_id': False,
                                     'token': False
                                 })
