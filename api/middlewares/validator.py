"""This file provides check() and @validate() functions.

Usage:
errors = check(document, schema)

or

@validate(schema)
def add(document) -> ServiceResponse:
    ...
"""

import functools
import operator
import re
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Tuple,
    Union,
    TypeVar,
    Set,
)

from api.errors import api_error, ApiError
from api.common import ServiceResponse, ServiceRequest, ServiceCallable

T = TypeVar("T")
ApiErrors = List[ApiError]
Document = Union[Dict, List]
Schema = dict
Stack = Dict[str, Any]
Checker = Callable[[str, Document, Schema], Tuple[ApiErrors, Stack]]

# This dict is defined for types mapping to be
# more readable for frontednd devs.
# I know it is mostly redundand...
# FIXME: Redundancy.
_TYPES: Dict[str, str] = {
    "dict": "object",
    "str": "string",
    "int": "integer",
    "bool": "boolean",
    "list": "list",
    "NoneType": "none",
}


def _to_js_type(element: T) -> str:
    """Using _TYPES dict translate python type name
    to more frontend friendly version."""
    return _TYPES[type(element).__name__]


def _dict(path: str, element: T, schema: Schema) -> Tuple[ApiErrors, Stack]:
    errors: ApiErrors = []
    stack: Stack = {}
    if not isinstance(element, dict):
        error = api_error(
            "invalid_type", extra_info=["object", _to_js_type(element)], field=path
        )
        return [error], {}

    for required_key in schema["required"]:
        if isinstance(required_key, str) and required_key not in element:
            error = api_error("required_key_missing", field=f"{path},{required_key}")
            errors.append(error)
        if (
            isinstance(required_key, dict)
            and required_key["required"] not in element
            and not all([k for k in required_key["unless"] if k in element])
        ):
            required = required_key["required"]
            errors.append(
                api_error(
                    "required_key_missing_unless",
                    [required_key["unless"]],
                    field=f"{path},{required}",
                )
            )

    for key in element.keys():
        if key not in schema.keys():
            error = api_error("unknown_field", field=f"{path},{key}")
            errors.append(error)
        else:
            stack.update({f"{path},{key}": element[key]})  # type: ignore
    return errors, stack


def _list(path: str, element: T, schema: Schema) -> Tuple[ApiErrors, Stack]:
    errors: ApiErrors = []
    stack: Stack = {}

    if not isinstance(element, list):
        error = api_error(
            "invalid_type", extra_info=["list", _to_js_type(element)], field=path
        )
        return [error], {}

    # Ends check, because it would check as many times as len(element) so it could be
    # infinity.
    if len(element) > schema["max_elements"]:
        error = api_error(
            "list_too_big", extra_info=[schema["max_elements"]], field=path
        )
        errors.append(error)
        return errors, stack

    # If we have only one element in list than we don't have to check.
    if not schema.get("allow_duplicates") and not len(element) < 1:
        seen: Set[T] = set()
        for i, e in enumerate(element):
            if not isinstance(e, (dict, list)):
                if e not in seen:
                    seen.add(e)
                else:
                    errors.append(
                        api_error(
                            "duplicate_entry", extra_info=[e], field=f"{path}.{i}"
                        )
                    )
            else:
                stack.update({f"{path},{i}": e})

        for i, e in enumerate(seen):
            stack.update({f"{path},{i}": e})

    for i, e in enumerate(element):
        stack.update({f"{path},{i}": e})

    return errors, stack


def _string(path: str, element: T, schema: Schema) -> Tuple[ApiErrors, Stack]:
    errors: ApiErrors = []
    min_lenght = schema.get("min")
    max_lenght = schema.get("max")
    pattern = schema.get("pattern")

    if not isinstance(element, str):
        error = api_error(
            "invalid_type", extra_info=["string", _to_js_type(element)], field=path
        )
        return [error], {}

    if min_lenght and len(element) < min_lenght:
        error = api_error("string_too_short", extra_info=[f"{min_lenght}"], field=path)
        errors.append(error)

    if max_lenght and len(element) > max_lenght:
        error = api_error(
            "string_too_long", extra_info=[f"{max_lenght} (exclusive)"], field=path
        )
        errors.append(error)

    if pattern:
        if not re.match(pattern, element):
            error = api_error("pattern_mismatch", extra_info=[pattern], field=path)
            errors.append(error)

    return errors, {}


def _integer(path: str, element: T, schema: Schema) -> Tuple[ApiErrors, Stack]:
    errors: ApiErrors = []
    min_value = schema.get("min")
    max_value = schema.get("max")

    if not isinstance(element, int):
        error = api_error(
            "invalid_type", extra_info=["int", _to_js_type(element)], field=path
        )
        return [error], {}

    if min_value and element < min_value:
        error = api_error("number_too_low", extra_info=[f"{min_value}"], field=path)
        errors.append(error)

    if max_value and element > max_value:
        error = api_error("number_too_high", extra_info=[f"{max_value}"], field=path)
        errors.append(error)

    return errors, {}


def _enum(path: str, element: T, schema: Schema) -> Tuple[ApiErrors, Stack]:
    errors: ApiErrors = []
    values = schema["values"]
    if element not in values:
        error = api_error("invalid_value", extra_info=[values], field=path)
        errors.append(error)
    return errors, {}


def _boolean(path: str, element: T, schema: Schema) -> Tuple[ApiErrors, Stack]:
    errors: ApiErrors = []
    if not isinstance(element, bool):
        element_type = _to_js_type(element)
        error = api_error("invalid_type", extra_info=["int", element_type], field=path)
        errors.append(error)
    return errors, {}


_CHECKERS: Dict[str, Checker] = {
    "dict": _dict,
    "list": _list,
    "str": _string,
    "int": _integer,
    "enum": _enum,
    "bool": _boolean,
}


def _get_nested_schema_item(schema: Schema, path: str) -> Any:
    """Gets nested schema item from schema by path.
    Comma: , is used as a separator to prevent collisions with embeds' names.

    Example:
    >>> _get_nested_schema_item([{'foo':'bar'}], path: '0,foo')
    'bar'
    >>> _get_nested_schema_item({'a':{'b':'c'}}, path: 'a,b')
    'c'
    """
    # Substitute number to '_items' to get sub_schema for every list index.
    path_list = ["_items" if item.isdigit() else item for item in path.split(",")]

    # Type is ignored because operator.getitem() does not support string as a key.
    # But is needed for getting dict item.
    return functools.reduce(
        operator.getitem,  # type: ignore
        path_list,
        schema,
    )


def check(document: Document, schema: Schema, data_prefix: str = "data") -> ApiErrors:

    _schema = {data_prefix: schema}
    stack: Stack = {data_prefix: document}
    errors: ApiErrors = []

    while stack:
        path, element = stack.popitem()

        current_schema: Schema = _get_nested_schema_item(  # type: ignore
            _schema, path
        )

        if not document:
            return [
                api_error("required_key_missing", field=f"{data_prefix}.{rk}")
                for rk in current_schema["required"]
            ]

        sub_check = _CHECKERS[current_schema["_type"]](path, element, current_schema)

        errors += sub_check[0]
        stack.update(sub_check[1])
        # Replace , with . for clarity.
        for e in errors:
            if "field" in e:
                e["field"] = e["field"].replace(",", ".")  # type: ignore
    return errors


def validate(schema: Schema, data_prefix: str = "data") -> Callable:
    """Provides decorator interface for check().

    Decorated function must look like ServiceCallable and first function argument will be
    checked eg.
    >>> @validate(schema)
    >>> def my_add_service(request: ServiceRequest) -> ServiceResponse: ...
    """

    def inner(f: ServiceCallable):
        @functools.wraps(f)
        def wraper(
            request: ServiceRequest, *args, **kwargs
        ) -> Union[ServiceResponse, ServiceCallable]:
            errors: ApiErrors = check(
                request.content, schema, data_prefix
            )  # type: ignore
            response = ServiceResponse(422, errors=errors)
            return f(request, *args, **kwargs) if not errors else response

        return wraper

    return inner
