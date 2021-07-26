from dataclasses import dataclass
from typing import Any, Dict

from typing_extensions import Literal

Sort = Dict[str, Literal[-1, 1]]
Projection = Dict[str, bool]


class FindQuery():
    def __init__(self,
                 _filter=None,
                 projection=None,
                 sort=None,
                 limit=10,
                 skip=0,
                 embed=None):
        if not _filter:
            self._filter = {}
        else:
            self._filter = _filter

        if not sort:
            self.sort = {'_id': 1}
        else:
            self.sort = sort

        if not projection:
            self.projection = None
        else:
            self.projection = projection
        if not embed:
            self.embed = None
        self.limit = limit
        self.skip = skip


@dataclass
class UserSession:
    _id: int
    token: str
    user_id: int
    exp: int
    role: int