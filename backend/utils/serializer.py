from datetime import datetime

from bson import ObjectId


def _serialize_value(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(val) for key, val in value.items()}
    return value


def serialize_document(document: dict):
    if document is None:
        return None
    return _serialize_value(document)


def serialize_many(documents: list):
    return [serialize_document(doc) for doc in documents]
