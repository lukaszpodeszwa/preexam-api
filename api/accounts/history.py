from typing import Dict, List, Tuple

import api.database as db
from api.common.service import ServiceRequest, ServiceResponse
from api.errors import api_error
from api.middlewares import require_auth


def _aggregate_history(
    skip: int, limit: int, user_id: int, sort: Dict
) -> Tuple[List, bool]:
    pipeline = [
        {"$match": {"_id": user_id}},
        {"$project": {"history": 1, "show_history": 1}},
        {"$sort": sort},
    ]

    res = list(db.db.accounts.aggregate(pipeline))[0]
    if res.get("history"):
        return res["history"], res.get("show_history")
    else:
        return [], res.get("show_history")


@require_auth()
def find(r: ServiceRequest, account_id: int) -> ServiceResponse:
    sort = {}
    for key, value in r.query.sort.items():
        sort[f"history.{key}"] = value
    res, show_history = _aggregate_history(
        r.query.skip, r.query.limit, account_id, sort
    )
    if show_history:
        return ServiceResponse(200, res)
    return ServiceResponse(200, [])


@require_auth()
def find_many_mine(r: ServiceRequest) -> ServiceResponse:
    sort = {}
    for key, value in r.query.sort.items():
        sort[f"history.{key}"] = value
    res, show_history = _aggregate_history(
        r.query.skip, r.query.limit, r.user_session.user_id, sort
    )
    return ServiceResponse(200, res)


def add(element: Dict, user_id: int) -> ServiceResponse:
    """Adds element to user history. Internal use only."""
    # Unset 100th element and delete id.
    # TODO: Refactor.
    db.db.accounts.update_one(
        {"_id": user_id},
        {
            "$push": {"history": element},
        },
    )
    return ServiceResponse(204)
