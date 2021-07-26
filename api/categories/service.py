"""
https://gitlab.com/preexam/api/-/issues/12

Caregories are embeded with one another using two keys:

  parent_id      - defines upper category.
  main_parent_id - defines highest category. Eg. main_parent for category
                   Trigonometry is Maths.
                   Main parents have parent_id and main_parent_id set to 0.
"""

from typing import List

import api.categories.schema as schema
from api import database
from api.common import ServiceRequest, ServiceResponse
from api.middlewares import require_auth, validate

database.Embed('category', 'category_id', 'categories')
# NOTE: associate_categories embed is after get_categories_list function


@validate(schema.NEW_CATEGORY)
@require_auth('mod')
def new(r: ServiceRequest) -> ServiceResponse:
    # If creating main parent.
    if r.content['parent_id'] == 0:
        r.content['main_parent_id'] = 0
        return database.insert_one('categories', r.content)

    parent_cat_res = database.find_one_by_id('categories',
                                             r.content['parent_id'])
    if parent_cat_res.errors:
        return parent_cat_res
    parent = parent_cat_res.response
    # If parent is main parent then take its id as a main_parent_id.
    if parent['main_parent_id'] == 0:
        r.content['main_parent_id'] = parent['_id']
    # Inharit main_parent_id from parent.
    else:
        r.content['main_parent_id'] = parent['main_parent_id']

    return database.insert_one('categories', r.content)


@validate(schema.UPDATE_CATEGORY)
@require_auth('mod', entity='category')
def update(r: ServiceRequest, category_id: int) -> ServiceResponse:
    if r.content.get('parent_id') and r.content['parent_id'] == 0:
        r.content['main_parent_id'] = 0
        return database.update_one('categories', category_id, r.content)

    if r.content.get('parent_id'):
        parent_cat_res = database.find_one_by_id('categories',
                                                 r.content['parent_id'])
        if parent_cat_res.errors:
            return parent_cat_res

        parent = parent_cat_res.response
        # If parent is main parent then take its id as a main_parent_id.
        if parent['main_parent_id'] == 0:
            r.content['main_parent_id'] = parent['_id']
        # Inharit main_parent_id from parent.
        else:
            r.content['main_parent_id'] = parent['main_parent_id']
    return database.update_one('categories', category_id, r.content)


@require_auth()
def get(r: ServiceRequest, category_id: int) -> ServiceResponse:
    """Get single category."""
    return database.find_one_by_id('categories', category_id,
                                   {'main_parent_id_id': False})


@require_auth()
def associated_categories(r: ServiceRequest,
                          category_id: int) -> ServiceResponse:
    """Get list of sorterd categories associated with given category.
    'Embeding' is done is done in opposite direction meaning that
    category we're embeding to is first and main parent is last and after
    this list is reversed.
    """
    category_req = get(r, category_id)
    if category_req.errors:
        return category_req
    category = category_req.response
    # Nothing to embed.
    if category['main_parent_id'] == 0:
        return ServiceResponse(200, [category])

    # Gets all categories with same main parent.
    # If we would have thousends of them it might be problem, but now isn't.
    associated_categories: List[dict] = database.find(
        'categories', {
            'main_parent_id': category['main_parent_id']
        }, {
            'main_parent_id': False
        }).response
    main_parent = database.find_one_by_id('categories',
                                          category['main_parent_id']).response
    associated_categories.append(main_parent)
    sorted_categories: List[dict] = [category]
    parent_id = category['parent_id']

    while associated_categories:
        parent = {}
        # Search for next parent.
        for c in associated_categories:
            if c['_id'] == parent_id:
                parent = c
                break
        sorted_categories.append(parent)

        # Break if parent is main parent.
        if parent['parent_id'] == 0:
            break
        associated_categories.remove(parent)
        parent_id = parent['parent_id']

    return ServiceResponse(200, list(reversed(sorted_categories)))


def associated_categories_embed(category_id) -> List[dict]:
    """I wanted to use functools.partial() but then i have no way to
       ommit response wrapping by ServiceResponse."""
    res = associated_categories(
        ServiceRequest({}, {}),  # type: ignore
        category_id)
    if res.errors:
        return []
    return res.response


database.FuncEmbed('associated_categories', 'category_id',
                   associated_categories_embed)


@require_auth()
def search(r: ServiceRequest) -> ServiceResponse:
    if r.query.projection:
        r.query.projection['main_parent_id_id'] = False
    return database.find_with_query('categories', r.query)


@require_auth('mod', entity='category')
def delete(r: ServiceRequest, category_id: int) -> ServiceResponse:
    return database.delete_one('categories', category_id)
