import time

BLOCK_ACCOUNT = {
    "_type": "dict",
    "required": ["blocked_to", "blocked_for"],
    "blocked_to": {
        "_type": "int",
        # Minimalny czas blokady konta to 1 godzina.
        "min": int(time.time()) + 3600,
        "desc": "Unixowy timestamp. Określa do kiedy konto jest zablokowane.",
    },
    "blocked_for": {"_type": "str", "desc": "Za co user dostał bana."},
}

CHANGE_ROLE = {
    "_type": "dict",
    "required": ["role"],
    "role": {
        "_type": "enum",
        "values": ["admin", "mod", "user"]
    }
}

ACCOUNTS_QUERY = {
    "_type": "dict",
    "required": [],
    "exclude": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "enum",
            "values": [
                "_id",
                "blocked_for",
                "blocked_to",
                "email",
                "username",
                "name",
                "last_name",
                "newsletter",
            ],
        },
    },
    "sort": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "enum",
            "values": [
                "_id",
                "blocked_for",
                "blocked_to",
                "email",
                "username",
                "name",
                "last_name",
                "newsletter",
            ],
        },
    },
    "limit": {"_type": "int", "min": 1, "max": 200,},
    "skip": {"_type": "int", "min": 1,},
    "_id": {"_type": "list", "max_elements": 100, "_items": {"_type": "int",}},
    "blocked_to": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "int",
            "desc": "Unixowy timestamp. Określa do kiedy konto jest zablokowane.",
        },
    },
    "blocked_for": {"_type": "list", "max_elements": 20, "_items": {"_type": "str"}},
    "email": {
        "_type": "list",
        "max_elements": 20,
        "_items": {"_type": "str", "min": 5, "pattern": r"^\S+?@\S+?\.\S+?$",},
    },
    "username": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "str",
            "min": 4,
            "max": 30,
            "pattern": r"^[a-źA-Ź-._0-9]+?$",
        },
    },
    "name": {
        "_type": "list",
        "_items": {"_type": "str", "min": 4, "max": 30, "pattern": r"^[a-źA-Ź]+?$"},
    },
    "last_name": {
        "_type": "list",
        "_items": {"_type": "str", "min": 4, "max": 30, "pattern": r"^[a-źA-Ź]+?$"},
    },
    "newsletter": {"_type": "list", "_items": {"_type": "bool"}},
    "show_history": {"_type": "list", "_items": {"_type": "bool"}},
}

