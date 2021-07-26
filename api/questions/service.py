import time
from typing import Any, Dict, List, Optional

import api.categories as categories
import api.categories.service as categoreis
import api.database as db
import api.images.service as images
from api.common import ServiceRequest, ServiceResponse
from api.errors import ApiError, api_error
from api.middlewares import require_auth, validate
from api.questions import schema

db.Embed('questions', 'questions_ids', 'questions', is_array=True)


@validate(schema.QUESTION)
@require_auth('mod')
def add(r: ServiceRequest) -> ServiceResponse:
    r.content['created_at'] = int(time.time())
    r.content['author_id'] = r.user_session.user_id
    cat_req = categoreis.get(r, r.content['category_id'])
    if cat_req.errors:
        return cat_req

    def check_if_image_exists(image_id: int, field: str) -> Optional[ApiError]:
        error: ApiError = images.get_author(  # type: ignore
            r, image_id).errors
        if error:
            error['field'] = field  # type: ignore
            error['entities'] = [image_id]
            return error
        return None

    if 'image_id' in r.content:
        error = check_if_image_exists(r.content['image_id'], 'data.image_id')
        if error:
            return ServiceResponse(404, errors=error)

    cat_req = categoreis.get(r, r.content['category_id'])
    if cat_req.errors:
        return cat_req

    if 'sub_questions' in r.content:
        errors: List[ApiError] = [
            check_if_image_exists(  # type: ignore
                subq['image_id'], f'sub_questions.{index}.image_id')
            for index, subq in enumerate(r.content['sub_questions'])
            if 'image_id' in subq
        ]
        if any(errors):
            return ServiceResponse(404, errors=errors)

        for i in range(len(r.content['sub_questions'])):
            r.content['sub_questions'][i]['_id'] = i + 1

    return db.insert_one('questions', r.content)


@require_auth()
def find_one(r: ServiceRequest, question_id: int) -> ServiceResponse:
    res = db.find_one_by_id('questions', question_id, r.query.projection,
                            r.query.embed)
    if res.errors:
        return res
    if r.user_session.role == 'user':
        if not res.response.get('view_correct_answers'):
            if 'correct_answers' in res.response:
                del res.response['correct_answers']

            if 'sub_questions' in res.response:
                for i in range(len(res.response['sub_questions'])):
                    del res.response['sub_questions'][i]['correct_answers']
    return res


@require_auth()
def find_many(r: ServiceRequest) -> ServiceResponse:
    res = db.find_with_query('questions', r.query)
    if res.errors:
        return res
    if r.user_session.role == 'user':
        if not res.response.get('view_correct_answers'):
            if 'correct_answers' in res.response:
                del res.response['correct_answers']

            if 'sub_questions' in res.response:
                for i in range(len(res.response['sub_questions'])):
                    del res.response['sub_questions'][i]['correct_answers']
    return res


@validate(schema.UPDATE_QUESTION)
@require_auth('mod')
def update_one(r: ServiceRequest, question_id: int) -> ServiceResponse:
    return db.update_one('questions', question_id, r.content)


@validate(schema.CHECK)
@require_auth()
def check(r: ServiceRequest, question_id: int) -> ServiceResponse:
    response = db.find_one_by_id('questions', question_id)
    if response.errors:
        return response

    correct_answer = response.response.get('correct_answers')
    if not correct_answer:
        correct_answer = [response.response.get('correct_answer')]

    if correct_answer == r.content['answers']:
        return ServiceResponse(200, {'correct': True})
    else:
        if response.response.get('view_correct_answers'):
            return ServiceResponse(200, {
                'correct': False,
                'correct_answer': correct_answer
            })
        return ServiceResponse(200, {'correct': False})
