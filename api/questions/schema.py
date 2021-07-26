from api.common.schema import delete_required
import api.database

QUESTION = {
    '_type':
    'dict',
    'required': [
        'category_id',
        'text',
        'view_correct_answers',
        {
            "required": "sub_questions",
            "unless": ["answers", "correct_answers"]
        },
        {
            "required": "answers",
            "unless": "sub_questions"
        },
        {
            "required": "correct_answers",
            "unless": "sub_questions"
        },
    ],
    'category_id': {
        '_type': 'int'
    },
    'text': {
        '_type': 'str',
        'min': 1,
        'max': 400,
    },
    'content': {
        '_type': 'str',
        'min': 1,
        'max': 1000,
    },
    'sub_questions': {
        '_type': 'list',
        'max_elements': 10,
        '_items': {
            '_type': 'dict',
            'required': ['text', 'answers', 'correct_answers'],
            'text': {
                '_type': 'str',
                'min': 1,
                'max': 400,
            },
            'content': {
                '_type': 'str',
                'min': 1,
                'max': 1000,
            },
            'answers': {
                '_type': 'list',
                'max_elements': 4,
                '_items': {
                    '_type': 'str',
                    'min': 1,
                    'max': 230,
                },
            },
            'correct_answers': {
                '_type': 'list',
                'max_elements': 5,
                '_items': {
                    '_type': 'int',
                    'min': 0,
                    'max': 3,
                }
            },
            'image_id': {
                '_type': 'int',
            },
            'hint': {
                '_type': 'str',
                'min': 1,
                'max': 100,
            },
        }
    },
    'answers': {
        '_type': 'list',
        'max_elements': 4,
        '_items': {
            '_type': 'str',
            'min': 1,
            'max': 230,
        },
    },
    'correct_answers': {
        '_type': 'list',
        'max_elements': 5,
        '_items': {
            '_type': 'int',
            'min': 0,
            'max': 3,
        }
    },
    'image_id': {
        '_type': 'int',
    },
    'hint': {
        '_type': 'str',
        'min': 1,
        'max': 100,
    },
    'view_correct_answers': {
        '_type': 'bool'
    }
}

UPDATE_QUESTION = delete_required(QUESTION)

QUESTIONS_QUERY = {
    '_type': 'dict',
    'required': [],
    'exclude': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'enum',
            'values':
            ['_id', 'category_id', 'text', 'answers', 'hint', 'title'],
        }
    },
    'sort': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type':
            'enum',
            'values': [
                'category', 'text', 'answers', 'hint', '-category', '-text',
                '-answers', '-hint', '-_id', 'title'
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
    'category_id': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'int',
        }
    },
    'created_at': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'int',
        }
    },
    'author_id': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'int',
        }
    },
    'text': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'str',
            'min': 1,
            'max': 70,
        },
    },
    'answers': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'str',
            'min': 1,
            'max': 60,
        },
    },
    'hint': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'str',
            'min': 1,
            'max': 60,
        }
    },
    'category.name': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'str',
        },
    },
    'category.parent_id': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'str',
        },
    },
    'category.main_parent_id': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'str',
        },
    },
    'embed': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'enum',
            'values': ['category', 'associated_categories', 'author'],
        }
    }
}

SINGLE_QUESTION_QUERY = {
    '_type': 'dict',
    'required': [],
    'exclude': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'enum',
            'values':
            ['_id', 'category_id', 'text', 'answers', 'hint', 'title'],
        }
    },
    'embed': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type': 'enum',
            'values': ['category', 'associated_categories', 'author'],
        }
    }
}

CHECK = {
    '_type': 'dict',
    'required': ['answers'],
    'answers': {
        '_type': 'list',
        'max_elements': 5,
        '_items': {
            '_type': 'int'
        }
    }
}