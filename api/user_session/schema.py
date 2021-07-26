LOGIN = {
    '_type': 'dict',
    'required': ['email', 'password'],
    'email': {
        '_type': 'str',
        'min': 5,
        'pattern': r'^\S+?@\S+?\.\S+?$',
    },
    'password': {
        '_type': 'str',
        # 'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$',
    }
}
