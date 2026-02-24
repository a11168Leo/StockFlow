import importlib
import sys

import mongomock
import pymongo
import pytest
from fastapi.testclient import TestClient

APP_MODULE = None


@pytest.fixture
def test_client(monkeypatch):
    global APP_MODULE

    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGO_DB_NAME", "stockflow_test")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
    monkeypatch.setattr(pymongo, "MongoClient", mongomock.MongoClient)

    if APP_MODULE is None:
        for module_name in list(sys.modules):
            if module_name == "backend" or module_name.startswith("backend."):
                del sys.modules[module_name]
        APP_MODULE = importlib.import_module("backend.api.main")

    for collection_name in APP_MODULE.mongodb.db.list_collection_names():
        APP_MODULE.mongodb.db[collection_name].delete_many({})

    with TestClient(APP_MODULE.app) as client:
        yield client
