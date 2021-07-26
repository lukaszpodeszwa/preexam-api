from typing import List

import api.common.rest as rest
import api.quizzes.solve as solve
from api.quizzes import service
from api.quizzes.schema import QUIZZES_QUERY, SINGLE_QUIZ_QUERY

endpoints: List[rest.ResourceEndpoint] = [
    rest.get('/quizzes', service.find, query_schema=QUIZZES_QUERY),
    rest.get('/quizzes/<int:quiz_id>',
             service.find_one,
             query_schema=SINGLE_QUIZ_QUERY),
    rest.post('/quizzes', service.add),
    rest.patch('/quizzes/<int:quiz_id>', service.update),
    rest.delete('/quizzes/<int:quiz_id>', service.delete),
    rest.post('/quizzes/<int:quiz_id>/solve', solve.start),
    rest.post('/quizzes/single_answer', solve.single_answer),
    rest.post('/quizzes/bulk_answer', solve.bulk_answer),
]
