import api.common.schema

NEW_CATEGORY = {
    '_type': 'dict',
    'required': ['name', 'parent_id'],
    'name': {
        '_type': 'str',
    },
    'parent_id': {
        '_type': 'int'
    }
}

CATEGORY = {
    '_type': 'dict',
    'required': ['name', 'parent_id', 'main_parent_id'],
    'name': {
        '_type': 'str',
    },
    'parent_id': {
        '_type': 'int'
    },
    'main_parent_id': {
        '_type': 'int'
    },
}

UPDATE_CATEGORY = api.common.schema.delete_required(NEW_CATEGORY)

CATEGORIES_QUERY = {
    '_type': 'dict',
    'required': [],
    'exclude': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'enum',
            'values': ['_id', 'name', 'parent_id'],
        }
    },
    'sort': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'enum',
            'values': [
                '_id'
                'name',
                'parent_id',
                '-parent_id',
                '-name',
                '-_id',
            ],
        }
    },
    'limit': {
        '_type': 'int',
        'min': 1,
        'max': 200,
    },
    'skip': {
        '_type': 'int',
        'min': 1,
    },
    '_id': {
        '_type': 'list',
        'max_elements': 100,
        '_items': {
            '_type': 'int',
        }
    },
    'name': {
        '_type': 'list',
        'max_elements': 100,
        '_items': {
            '_type': 'str',
        }
    },
    'parent_id': {
        '_type': 'list',
        'max_elements': 100,
        '_items': {
            '_type': 'int',
        }
    },
}

SINGLE_CATEGORY_QUERY = {
    '_type': 'dict',
    'required': [],
    'exclude': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'enum',
            'values': ['_id', 'name', 'parent_id'],
        }
    },
}