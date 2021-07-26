import copy

ACCOUNT = {
    '_type':
    'dict',
    'required':
    ['email', 'username', 'password', 'name', 'last_name', 'newsletter'],
    'email': {
        '_type': 'str',
        'min': 5,
        'pattern': r'^\S+?@\S+?\.\S+?$',
    },
    'username': {
        '_type': 'str',
        'min': 4,
        'max': 30,
        'pattern': r'^[a-źA-Ź-._0-9]+?$'
    },
    'name': {
        '_type': 'str',
        'min': 4,
        'max': 30,
        'pattern': r'^[a-źA-Ź]+?$'
    },
    'last_name': {
        '_type': 'str',
        'min': 4,
        'max': 30,
        'pattern': r'^[a-źA-Ź]+?$'
    },
    'password': {
        '_type': 'str',
        'min': 7,
        'max': 31,
        # 'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$',
    },
    'newsletter': {
        '_type': 'bool'
    },
    'show_history': {
        '_type': 'bool'
    }
}

UPDATE_ACCOUNT = copy.copy(ACCOUNT)
del UPDATE_ACCOUNT['password']
del UPDATE_ACCOUNT['email']
UPDATE_ACCOUNT['required'] = []

ACTIVATE_ACCOUNT = {
    '_type': 'dict',
    'required': ['code'],
    'code': {
        '_type': 'str',
        'pattern': r'^[0-9]{3}-[0-9]{3}-[0-9]{3}$',
    }
}

FORGOT_PASSWORD = {
    '_type': 'dict',
    'required': ['email'],
    'email': {
        '_type': 'str',
        'min': 5,
        'pattern': r'^\S+?@\S+?\.\S+?$',
    }
}

CONFIRM_FORGOT_PASWORD_CHANGE = {
    '_type': 'dict',
    'required': ['code', 'new_password', 'email'],
    'code': {
        '_type': 'str',
        'pattern': r'[a-z0-9]'
    },
    'email': {
        '_type': 'str',
        'min': 5,
        'pattern': r'^\S+?@\S+?\.\S+?$',
    },
    'new_password': {
        '_type': 'str',
        'min': 7,
        'max': 31,
        # 'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$',
    }
}

HISTORY_QUERY = {
    '_type': 'dict',
    'required': [],
    'limit': {
        '_type': 'int',
        'min': 1,
        'max': 200,
    },
    'skip': {
        '_type': 'int',
        'min': 1,
    },
    'sort': {
        '_type': 'list',
        'max_elements': 20,
        '_items': {
            '_type':
            'enum',
            'values': [
                'quiz_id', 'out_of', 'correct_answers', 'started_at',
                'ended_at', '-quiz_id', '-out_of', '-correct_answers',
                '-started_at', '-ended_at'
            ],
        }
    },
}

QUICK_PASSWORD_CHANGE = {
    '_type': 'dict',
    'required': ['old_password', 'new_password'],
    'old_password': {
        '_type': 'str',
        'min': 7,
        'max': 31,
        # 'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$',
    },
    'new_password': {
        '_type': 'str',
        'min': 7,
        'max': 31,
        # 'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$',
    }
}