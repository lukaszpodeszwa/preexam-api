import time
from typing import List, Optional

import api.database as database
import api.quizzes.schema as schema
from api.common.service import ServiceRequest, ServiceResponse
from api.errors import api_error, ApiError
from api.middlewares import require_auth, validate
import api.questions


def _find_questions(questions_ids: List[int]) -> Optional[ServiceResponse]:
    found_questions = database.db.questions.find(
        {'_id': {
            '$in': [id for id in questions_ids]
        }})

    found_questions_ids = [question['_id'] for question in found_questions]

    not_found = []
    for quiz_id in questions_ids:
        if quiz_id not in found_questions_ids:
            not_found.append(quiz_id)

    if not_found:
        return ServiceResponse(404,
                               errors=api_error('questions_not_found',
                                                entities=not_found))
    return None


@validate(schema.QUIZ)
@require_auth('mod')
def add(r: ServiceRequest) -> ServiceResponse:
    error = _find_questions(r.content['questions_ids'])
    if error:
        return ServiceResponse(404, errors=api_error('questions_not_found'))

    r.content['created_at'] = int(time.time())
    r.content['author_id'] = r.user_session.user_id
    return database.insert_one('quizzes', r.content) if not error else error


@require_auth()
def find(r: ServiceRequest) -> ServiceResponse:
    return database.find_with_query('quizzes', r.query)


@require_auth()
def find_one(r: ServiceRequest, quiz_id: int) -> ServiceResponse:
    return database.find_one_by_id('quizzes', quiz_id, r.query.projection,
                                   r.query.embed)


@require_auth('mod')
def delete(r: ServiceRequest, quiz_id: int) -> ServiceResponse:
    return database.delete_one('quizzes', quiz_id)


@validate(schema.UPDATE_QUIZ)
@require_auth('mod')
def update(r: ServiceRequest, quiz_id: int) -> ServiceResponse:
    error = _find_questions(r.content['questions_ids'])
    if error:
        return ServiceResponse(404, errors=api_error('questions_not_found'))
    return database.update_one('quizzes', quiz_id,
                               r.content) if not error else error
