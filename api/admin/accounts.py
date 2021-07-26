import datetime

import api.admin.schema as schema
import api.database as db
import api.mailing as mailing
from api.accounts.service import forgot_password
from api.common.service import ServiceRequest, ServiceResponse
from api.errors import api_error
from api.middlewares.authentication import require_auth
from api.middlewares.validator import validate


@validate(schema.BLOCK_ACCOUNT)
@require_auth("admin")
def block(r: ServiceRequest, account_id: int) -> ServiceResponse:
    res = db.find_one_by_id("accounts", account_id)
    if res.errors:
        return res
    account = res.response

    if account["role"] == "admin":
        return ServiceResponse(403, errors=api_error("cannot_block_admin"))

    error = mailing.send_mail(
        account["email"],
        "Blokada konta w PreExam",
        mailing.ACCOUNT_BLOCKED,
        {
            "name": account["name"],
            "to": datetime.date.fromtimestamp(r.content["blocked_to"]).strftime(
                "%H:%M %d/%m/%Y"
            ),
            "reason": r.content["blocked_for"],
        },
    )
    if error:
        return ServiceResponse(500, errors=error)
    return db.update_one(
        "accounts",
        account_id,
        {
            "blocked": {
                "for": r.content["blocked_for"],
                "to": r.content["blocked_to"],
                "by": r.user_session.user_id,
            }
        },
    )


@require_auth("admin")
def unblock(r: ServiceRequest, account_id: int) -> ServiceResponse:
    return db.update_one(
        "accounts",
        account_id,
        {
            "blocked.to": None,
            "blocked.for": None,
            "unblocked_by": r.user_session.user_id,
        },
    )


@require_auth("admin")
def query(r: ServiceRequest) -> ServiceResponse:
    if isinstance(r.query.projection, dict):
        r.query.projection["password"] = False
        r.query.projection["history"] = False
    return db.find_with_query("accounts", r.query)


@require_auth("admin")
def init_password_change(r: ServiceRequest, account_id: int) -> ServiceResponse:
    db_query = db.find_one_by_id("accounts", account_id)
    if db_query.errors:
        return db_query
    r.content = {"email": db_query.response["email"]}
    return forgot_password(r)


@require_auth("admin")
def delete(r: ServiceRequest, account_id: int) -> ServiceResponse:
    """Deletes account by deleting it phisicaly from database and replaces 
       his/hers id with 0 to give info that author of this object is deleted."""
    res = db.find_one_by_id("accounts", account_id)
    if res.errors:
        return res
    account = res.response

    if account["role"] == "admin":
        return ServiceResponse(403, errors=api_error("cannot_delete_admin"))

    for col in db.db.collection_names():
        db.db[col].update_many({"author_id": account_id}, {"$set": {"author_id": 0}})
    db.delete_one("accounts", account_id)
    mailing.send_mail(
        account["email"], "Usunięcie konta w PreExam.", mailing.ACCOUNT_DELETED,
        {
            "first_name": account["name"]
        }
    )
    return ServiceResponse(204)

@validate(schema.CHANGE_ROLE)
@require_auth("admin")
def change_role(r: ServiceRequest, account_id: int) -> ServiceResponse:
    """"Change account role."""
    res = db.find_one_by_id("accounts", account_id)
    if res.errors:
        return res
    account = res.response

    if account["role"] == "admin":
        return ServiceResponse(403, errors=api_error("cannot_change_admins_role"))

    return db.update_one("accounts", account["_id"], {"role": r.content["role"]})