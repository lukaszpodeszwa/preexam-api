import time
from functools import wraps
from typing import Callable, Dict, Tuple

import api.database
from api.common import ServiceRequest, ServiceResponse, UserSession
from api.errors import ApiError, Optional, api_error

_ROLES: Dict[str, int] = {
    "admin": 3,
    "mod": 2,
    "user": 1,
}


def _check_role(
    session_token: str, required_role: str, entity: str = None
) -> Tuple[Optional[UserSession], Optional[ApiError]]:

    if not session_token:
        return None, api_error("login_required")

    resoult = api.database.db.session_tokens.find_one({"token": session_token})
    if not resoult:
        return None, api_error("invalid_session_token")

    if int(time.time()) > resoult["exp"]:
        api.database.delete_one("session_tokens", _id=resoult["_id"])
        return None, api_error("session_expired")

    if _ROLES[resoult["role"]] < _ROLES[required_role]:
        if entity:
            return None, api_error(f"{entity}_not_found")
        return None, api_error("invalid_role")
    user_session = UserSession(
        resoult["_id"],
        resoult["token"],
        resoult["user_id"],
        resoult["exp"],
        resoult["role"],
    )
    return user_session, None


def require_auth(min_role: str = "user", entity: str = None) -> Callable:
    def inner(f: Callable):
        @wraps(f)
        def wrapper(service_request: ServiceRequest, *args, **kwagrs):
            user_session, error = _check_role(
                service_request.session_token, min_role, entity
            )
            # I'll fix this later maybe....
            service_request.user_session = user_session  # type: ignore
            return (
                f(service_request, *args, **kwagrs)
                if not error
                else ServiceResponse(401, errors=error)
            )

        return wrapper

    return inner
