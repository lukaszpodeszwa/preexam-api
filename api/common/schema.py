from api.middlewares.validator import Schema
import copy

def delete_required(schema: Schema):
    new_schema = copy.copy(schema)
    new_schema['required'] = []
    return new_schema
