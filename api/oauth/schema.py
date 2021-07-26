VALIDATE_STATE = {
    '_type': 'dict',
    'required': ['state', 'nonce', 'code'],
    'code': {
        '_type': 'str'
    },
    'state': {
        '_type': 'str'
    },
    'nonce': {
        '_type': 'str'
    }
}