"""Test Lambda Handler"""
# pylint: disable=unused-import
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# mypy: ignore-errors
import os

from .lamb_data import TEvent
from .mocks.botoMock import BogoClient
from .mocks.mongoMock import BogusMongo
from .mocks.pymssqlMock import BogusSQL


def test_media_deserializer_jpeg(monkeypatch) -> None:
    """Test Place Holder"""
    os.environ["sql_host"] = "bevor-server.database.windows.net"
    os.environ["sql_uname"] = "dmitrievichlevin"
    os.environ["sql_pword"] = "Lmfuzzinao$1"
    os.environ["sql_db"] = "bevor_dir"
    os.environ["AWS_BUCKET"] = "bevor-media"
    import boto3
    import pymssql
    import pymongo
    from media_microservice.app import lambda_handler
    monkeypatch.setattr(boto3, "client", lambda x: BogoClient(x))
    monkeypatch.setattr(pymssql, "connect", lambda *_args: BogusSQL(*_args))
    monkeypatch.setattr(pymongo, "MongoClient", lambda *_args, **_kwargs: BogusMongo(*_args, **_kwargs))

    t = lambda_handler(TEvent, None)

    _id = t['body']['id']
    meta = t['body']['metadata']

    # Check id
    assert _id == BogusSQL.inserted['id']

    # Check metadata for correct entries
    assert [k in ["parent", "owner", "parentId", "path", "type", "created_at", "size"] for k in meta.keys()]

    # Check size of image
    assert meta['size'] == BogusSQL.inserted['file_size']
