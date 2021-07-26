from api.common.service import ServiceRequest, ServiceResponse
import api.database as db


def get(r: ServiceRequest) -> ServiceResponse:
    info = db.connect.client.server_info()
    if not info:
        return ServiceResponse(500, {"status": "FAILURE"})
    return ServiceResponse(200, {"status": "OK"})
