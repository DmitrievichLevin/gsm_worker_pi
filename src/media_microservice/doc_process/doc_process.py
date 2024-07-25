"""Mongo Document SubProcess"""
from __future__ import annotations

import os
from operator import itemgetter
from typing import Any

import bson
import pymongo

from ..sync_sub import SubProcess


class DocumentProcess(SubProcess):
    """Attach Uploaded Media to Parent Document"""
    connection: Any

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)
        uri = os.environ.get("MONGO_URI")
        db_name = os.environ.get("MONGO_DB_NAME")
        self.connection = pymongo.MongoClient(uri, uuidRepresentation="standard").get_database(db_name)

    def execute(self) -> None:
        """Parent Document Update

        Raises:
            KeyError: Parent Document doesn't exist
        """
        _id, doc, doc_path, doc_id = itemgetter("id", "doc", "doc_path", "doc_id")(self.deps['metadata'])

        # str->ObjectId
        doc_id = bson.ObjectId(doc_id)

        found = self.connection[doc].find_one_and_update(
            {'_id': doc_id}, {'$set': {f"{doc_path}": _id}}, return_document=pymongo.ReturnDocument.AFTER)

        if not found:
            raise KeyError(f"Expected {doc} Document id:{doc_id}, but found none.")

    def rollback(self) -> None:
        """No Rollback."""
        pass
