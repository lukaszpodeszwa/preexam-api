"""Wraps some of pymongo collection methods to return them as ServiceResponse.
It is realy useful in not complex resources as questions.
"""
from typing import Any, Dict, List

from api import api_error
from api.common import FindQuery, Projection, ServiceResponse, Sort
from api.database.connect import db
from api.database.embed import Embed, FuncEmbed, embeds_storage

Filter = Dict[str, Any]

# Store data
id_cache: Dict[str, int] = {}


def _parse_sort(sort: Sort):
    return [(key, value) for key, value in sort.items()]


def find(collection: str,
         _filter: Filter,
         projection: Projection = None,
         sort: Sort = None,
         skip: int = 0,
         limit: int = 10,
         embed: List[str] = None) -> ServiceResponse:
    """Basic find method.
       Used for wrapping by other functions eg. find_one, find_with_query etc."""
    # If any filter key contains '.' it means that we have to embed.
    if [k for k in _filter if '.' in k] or embed:
        if not embed:
            embed = []

        pipeline = [
            {
                "$match": _filter
            },
            {
                '$skip': skip
            },
            {
                '$limit': limit
            },
        ]
        if sort:
            pipeline.append({'$sort': sort})
        if projection:
            pipeline.insert(
                1,
                {'$project': projection},
            )

        # Embeds from query._filters.
        embeds_objs: List[Embed] = [
            embeds_storage[e.split('.')[0]] for e in _filter
            if '.' in e and isinstance(embeds_storage[e.split('.')[0]], Embed)
        ] + [
            # Embeds from query.embed.
            embeds_storage[e]
            for e in embed if isinstance(embeds_storage[e], Embed)
        ]

        # As above but with FuncEmbeds.
        func_embeds_objs: List[FuncEmbed] = [
            embeds_storage[e] for e in embed
            if isinstance(embeds_storage[e], FuncEmbed)
        ]

        # Add as lookups.
        for i, e in enumerate(embeds_objs):
            pipeline.insert(i, {'$lookup': e.to_query()})

        # When we embed we don't want local_fields to appear.
        # If local_field is in any FuncEmbebs local_fields it is not projected
        # because 1) FuncEmbed needs it to work 2) FuncEmbed will delete it.
        if embeds_objs and not func_embeds_objs:
            pipeline.append({
                "$project": {
                    e.local_filed: False
                    for e in embeds_objs if e.local_filed not in
                    [fe.local_filed for fe in func_embeds_objs]
                }
            })

        # Unwind embeded fields because they appear as array.
        for e in embeds_objs:
            if not e.is_array:
                pipeline.append({
                    '$unwind': {
                        'path': f'${e.name}',
                        'preserveNullAndEmptyArrays': True
                    }
                })

        if not embed:
            pipeline.append({"$project": {e.name: False for e in embeds_objs}})
        db_data = list(db[collection].aggregate(pipeline))

        total_count: int = 0
        if db_data:
            # Here we use previous pipeline with $lookups and staff
            # to get total documents count for pagination.
            match_index = pipeline.index({'$match': _filter})
            pipeline = pipeline[0:match_index]
            pipeline.append({'$count': 'total_count'})
            total_count = list(
                db[collection].aggregate(pipeline))[0]['total_count']

        # Addicionaly add FuncEmbeds.
        if func_embeds_objs and db_data:
            for fe in func_embeds_objs:
                for d in db_data:
                    d[fe.name] = fe.func(d[fe.local_filed])
                    del d[fe.local_filed]

        return ServiceResponse(200, db_data, total_count=total_count)

    if not sort:
        sort = _parse_sort({'_id': 1})
    else:
        sort = _parse_sort(sort)
    if not projection:
        projection = None
    db_data = db[collection].find(
        _filter, projection).skip(skip).limit(limit).sort(sort)
    total_count = db[collection].count_documents(_filter)
    return ServiceResponse(200, list(db_data), total_count=total_count)


def find_with_query(collection: str, query: FindQuery) -> ServiceResponse:
    resoult = find(collection,
                   query._filter,
                   query.projection,
                   query.sort,
                   skip=query.skip,
                   embed=query.embed,
                   limit=query.limit)
    return resoult


def find_one(collection: str,
             _filter: Filter,
             projection: Projection = None,
             embed: List[str] = None) -> ServiceResponse:
    if embed:
        res = find(collection, _filter, projection, limit=1, embed=embed)
        res.total_count = None
        return res
    resoult = db[collection].find_one(_filter, projection)
    error = None
    if not resoult:
        error = api_error(f'{collection[:-1]}_not_found')
    return ServiceResponse(200, resoult, error)


def find_one_by_id(collection: str,
                   _id: int,
                   projection: Projection = None,
                   embed: List[str] = None) -> ServiceResponse:
    resoult = find_one(collection, {'_id': _id}, projection, embed)
    return resoult


def update_one(collection: str, _id: int,
               update_body: Dict[str, Any]) -> ServiceResponse:
    resoult = db[collection].update_one({'_id': _id}, {'$set': update_body})
    error = None
    if resoult.matched_count == 0:
        error = api_error(f'{collection[:-1]}_not_found')

    if not error:
        return ServiceResponse(204, errors=error)
    return ServiceResponse(404)


def insert_one(collection: str, body: Dict[str, Any]) -> ServiceResponse:
    if collection in id_cache:
        last_document_id = id_cache[collection] + 1
        id_cache.update({collection: last_document_id})
    else:
        last_document = db[collection].find_one({}, sort=[('_id', -1)])
        if last_document:
            last_document_id = last_document['_id'] + 1
        else:
            last_document_id = 1
        id_cache.update({collection: last_document_id})
    body['_id'] = last_document_id
    update_resoult = db[collection].insert_one(body)

    error = None
    if update_resoult.inserted_id == 0:
        error = api_error('api_error')
    return ServiceResponse(201, {'id': body['_id']}, errors=error)


def delete_one(collection: str, _id: int) -> ServiceResponse:
    delete_resoult = db[collection].delete_one({'_id': _id})
    error = None
    if delete_resoult.deleted_count == 0:
        error = api_error(f'{collection[:-1]}_not_found', entities=[_id])

    if not error:
        return ServiceResponse(204, errors=error)
    else:
        return ServiceResponse(404, errors=error)
