from typing import List

from api.questions.schema import QUESTIONS_QUERY, SINGLE_QUESTION_QUERY
from api.common.rest import post, get, patch, ResourceEndpoint
from api.questions.service import add, find_many, find_one, update_one, check

endpoints: List[ResourceEndpoint] = [
    get('/questions', find_many, query_schema=QUESTIONS_QUERY),
    get('/questions/<int:question_id>',
        find_one,
        query_schema=SINGLE_QUESTION_QUERY),
    post('/questions', add),
    patch('/questions/<int:question_id>', update_one),
    post('/questions/<int:question_id>/check', check),
]
