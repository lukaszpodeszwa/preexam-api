from api.common.schema import delete_required
from copy import deepcopy

QUIZ = {
    "_type": "dict",
    "required": ["questions_ids", "title", "title", "category_id"],
    "title": {"_type": "str", "min": 5, "max": 100,},
    "category_id": {"_type": "int"},
    "questions_ids": {
        "_type": "list",
        "max_elements": 100,
        "_items": {"_type": "int",},
    },
    "is_exam": {"_type": "bool"},
    "minutes_to_solve": {"_type": "int"},
}

UPDATE_QUIZ = delete_required(QUIZ)

QUIZZES_QUERY = {
    "_type": "dict",
    "required": [],
    "exclude": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "enum",
            "values": [
                "questions_ids",
                "author_id",
                "created_at",
                "_id",
                "category_id",
            ],
        },
    },
    "sort": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "enum",
            "values": [
                "questions_ids",
                "author_id",
                "created_at",
                "-questions_ids",
                "-author_id",
                "-created_at",
            ],
        },
    },
    "limit": {"_type": "int", "min": 1, "max": 200,},
    "skip": {"_type": "int", "min": 1,},
    "_id": {"_type": "list", "max_elements": 100, "_items": {"_type": "int",}},
    "questions_ids": {
        "_type": "list",
        "max_elements": 100,
        "_items": {"_type": "int"},
    },
    "title": {
        "_type": "list",
        "max_elements": 100,
        "_items": {"_type": "str", "min": 5, "max": 100},
    },
    "created_at": {"_type": "list", "max_elements": 100, "_items": {"_type": "int",}},
    "author_id": {"_type": "list", "max_elements": 100, "_items": {"_type": "int",}},
    "is_exam": {"_type": "bool"},
    "minutes_to_solve": {"_type": "list", "max_elements": 100,},
    "category_id": {"_type": "list", "max_elements": 20, "_items": {"_type": "int",}},
    "category.name": {
        "_type": "list",
        "max_elements": 20,
        "_items": {"_type": "str",},
    },
    "category.parent_id": {
        "_type": "list",
        "max_elements": 20,
        "_items": {"_type": "int",},
    },
    "category.main_parent_id": {
        "_type": "list",
        "max_elements": 20,
        "_items": {"_type": "int",},
    },
    "embed": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "enum",
            "values": ["category", "associated_categories", "author", "questions"],
        },
    },
}

SINGLE_QUIZ_QUERY = {
    "_type": "dict",
    "required": [],
    "exclude": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "enum",
            "values": [
                "questions_ids",
                "author_id",
                "created_at",
                "_id",
                "category_id",
            ],
        },
    },
    "embed": {
        "_type": "list",
        "max_elements": 20,
        "_items": {
            "_type": "enum",
            "values": ["category", "associated_categories", "author", "questions"],
        },
    },
}

SUB_ANSWER = {
    "_type": "dict",
    "required": ["question_id", "answer_indexes"],
    "question_id": {"_type": "int"},
    "answer_indexes": {
        "_type": "list",
        "max_elements": 5,
        "_items": {"_type": "int", "min": -1, "max": 4},
    },
}


SINGLE_ANSWER = {
    "_type": "dict",
    "required": [
        {"required": "sub_answer", "unless": ["answer_indexes"]},
        {"required": "answer_indexes", "unless": ["sub_answer"]},
    ],
    "answer_indexes": {
        "_type": "list",
        "max_elements": 5,
        "_items": {"_type": "int", "min": -1, "max": 4},
    },
    "sub_answers": {"_type": "list", "max_elements": 10, "_items": SUB_ANSWER},
}


BULK_ANSWER_ITEM = deepcopy(SINGLE_ANSWER)
BULK_ANSWER_ITEM["required"].append("question_id")  # type: ignore
BULK_ANSWER_ITEM["question_id"] = {"_type": "int"}  # type: ignore

BULK_ANSWER = {
    "_type": "list",
    "max_elements": 100,
    "_items": BULK_ANSWER_ITEM,
}
