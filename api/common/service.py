from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union, TypeVar, Generic

from typing_extensions import TypedDict

from api.common.other import FindQuery, UserSession
from api.errors import ApiError


class ServiceRequest:
    def __init__(self,
                 content,
                 user_session: UserSession,
                 session_token: str = '',
                 query=FindQuery()):
        self.content = content
        self.user_session = user_session
        self.session_token = session_token
        self.query = query

    def __repr__(self):
        return str(self.__dict__)


@dataclass
class ServiceResponse:
    def __init__(self,
                 code: int,
                 response={},
                 errors: Optional[Union[List[ApiError], ApiError]] = None,
                 total_count: Optional[int] = None,
                 content_type: str = 'application/json'):
        self.code = code
        self.response = response
        self.errors = errors
        self.total_count = total_count
        self.content_type = content_type

    def __repr__(self):
        return str(self.__dict__)


ServiceCallable = Callable[..., ServiceResponse]
