from typing import List

import api.categories.schema as schema
from api.categories.service import (delete, get, associated_categories, new,
                                    search, update)
from api.common import rest

endpoints: List[rest.ResourceEndpoint] = [
    rest.post('/categories', new),
    rest.patch('/categories/<int:category_id>', update),
    rest.delete('/categories/<int:category_id>', delete),
    rest.get('/categories/<int:category_id>',
             get,
             query_schema=schema.SINGLE_CATEGORY_QUERY),
    rest.get('/categories/<int:category_id>/associated',
             associated_categories),
    rest.get('/categories', search, query_schema=schema.CATEGORIES_QUERY),
]
