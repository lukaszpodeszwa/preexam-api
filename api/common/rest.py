import json
import re
import urllib.parse
from functools import wraps
from typing import Callable, Dict, List, Tuple, Union

from flask import Response

import api.errors
from api.common.other import FindQuery
from api.common.service import ServiceCallable, ServiceRequest, ServiceResponse
from api.errors import api_error
from api.middlewares import check

ResourceEndpoint = Tuple[str, str, Callable, str]
ResourceEndpoints = List[ResourceEndpoint]

response = Response(mimetype='application/json')


def _to_regex(element: str) -> re.Pattern:
    return re.compile(element, re.IGNORECASE)


def _map_to_query(query: dict) -> FindQuery:
    mapped_query = FindQuery()
    for k, v in query.items():
        if k == 'exclude':
            mapped_query.projection = {field: False for field in v}

        if k == 'sort':
            mapped_query.sort = {
                # Strip '-' because: GET /questions?sort=-hint
                field.strip('-'): (-1 if '-' in field else 1)
                for field in v
            }

        # Map filters.
        if k not in ['exclude', 'sort', 'limit', 'skip', 'embed']:
            mapped_query._filter[k] = {
                '$in':
                [_to_regex(i) if not isinstance(i, int) else i for i in v]
            }

        if k == 'embed':
            mapped_query.embed = query['embed']
        if k == 'limit':
            mapped_query.limit = query['limit']
        if k == 'skip':
            mapped_query.skip = query['skip']
    return mapped_query


def _parse_service_response(sr: ServiceResponse) -> Response:
    response = Response(mimetype=sr.content_type)
    from flask import request
    if sr.errors:
        if not isinstance(sr.errors, list):
            sr.errors = [sr.errors]
        if 'pl' in str(request.headers.get('Accept-Language')):
            sr.errors = [api.errors.to_polish(e)
                         for e in sr.errors]  # type: ignore

        response.status_code = int(str(sr.code)[:3])
        response.data = json.dumps(sr.errors)
    elif sr.content_type == 'application/json':
        response.status_code = sr.code
        response.data = json.dumps(sr.response, ensure_ascii=False)
    else:
        response.status_code = sr.code
        response.data = sr.response

    if sr.total_count:
        response.headers['X-Total-Count'] = sr.total_count
    return response


def _service_wrapper(func: ServiceCallable,
                     method: str,
                     query_schema: dict = None,
                     content_type: str = 'application/json') -> Callable:
    @wraps(func)
    def wrapper(**kwargs):
        from flask import request
        auth_header = request.headers.get('Authorization')
        if auth_header:
            session_token: str = auth_header[7:]
        else:
            session_token = ''

        if method in ('post', 'patch'):
            if request.content_type != content_type:
                return _parse_service_response(
                    ServiceResponse(415,
                                    errors=api_error('unsupported_media_type',
                                                     [content_type])))

            if request.is_json and request.data:
                try:
                    json.loads(request.data)
                except json.JSONDecodeError:
                    return ServiceResponse(400,
                                           errors=api_error('invalid_json'))
                service_request = ServiceRequest(user_session={},
                                                 session_token=session_token,
                                                 content=request.json)
            else:
                service_request = ServiceRequest(user_session={},
                                                 session_token=session_token,
                                                 content=request.data)

        elif method == 'get':
            url_query = dict(
                urllib.parse.parse_qs(
                    urllib.parse.urlsplit(request.url).query))

            query = {}
            if url_query and query_schema:
                for k, v in url_query.items():
                    if k in ['limit', 'skip'] and v[0].isdigit():
                        query[k] = int(v[0])
                    elif k in ['limit', 'skip'] or isinstance(v, bool):
                        query[k] = v[0]
                    elif v == ['_true_']:
                        query[k] = True
                    elif v == ['_false_']:
                        query[k] = False
                    else:
                        query[k] = [int(i) if i.isdigit() else i for i in v]
                errors = check(query, query_schema, 'query')
                if errors:
                    return _parse_service_response(
                        ServiceResponse(422, errors=errors))
            mapped = _map_to_query(query)
            service_request = ServiceRequest(content={},
                                             user_session={},
                                             session_token=session_token,
                                             query=mapped)
        elif method == 'delete':
            service_request = ServiceRequest(content={},
                                             user_session={},
                                             session_token=session_token)

        return _parse_service_response(func(service_request, **kwargs))

    return wrapper


def post(url: str,
         func: ServiceCallable,
         content_type: str = 'application/json') -> ResourceEndpoint:
    endpoint = url.replace('/', '_') + 'post'
    view_func = _service_wrapper(func, 'post', content_type=content_type)
    return (url, endpoint, view_func, 'POST')


def patch(url: str,
          func: ServiceCallable,
          content_type: str = 'application/json') -> ResourceEndpoint:
    endpoint = url.replace('/', '_') + 'patch'
    view_func = _service_wrapper(func, 'patch', content_type=content_type)
    return (url, endpoint, view_func, 'PATCH')


def delete(url: str, func: ServiceCallable) -> ResourceEndpoint:
    endpoint = url.replace('/', '_') + 'delete'
    view_func = _service_wrapper(func, 'delete')
    return (url, endpoint, view_func, 'DELETE')


def get(url: str,
        func: ServiceCallable,
        query_schema=None) -> ResourceEndpoint:
    endpoint = url.replace('/', '_') + 'get'
    view_func = _service_wrapper(func, 'get', query_schema=query_schema)
    return (url, endpoint, view_func, 'GET')
