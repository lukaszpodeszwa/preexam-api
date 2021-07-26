import api.database
from api.common import ServiceRequest, ServiceResponse
from api.errors import api_error
from api.middlewares import require_auth, validate


@require_auth()
def mine_current_quiz(req: ServiceRequest) -> ServiceResponse:
    return api.database.find_one_by_id('accounts', req.user_session.user_id,
                                       {'current_quiz': True})
