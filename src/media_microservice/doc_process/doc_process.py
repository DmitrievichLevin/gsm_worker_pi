"""Mongo Document SubProcess"""
from __future__ import annotations

import os
import uuid
from operator import itemgetter
from typing import Any

import pymongo

from ..sync_sub import SubProcess


class DocumentProcess(SubProcess):
    """Attach Uploaded Media to Parent Document"""
    connection: Any

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)
        uri = os.environ.get("MONGO_URI")
        db_name = os.environ.get("MONGO_DB_NAME")
        self.connection = pymongo.MongoClient(host=uri).get_database(db_name)

    def execute(self) -> None:
        """Parent Document Update

        Raises:
            KeyError: Parent Document doesn't exist
        """
        _id, doc, doc_path, doc_id = itemgetter("id", "doc", "doc_path", "doc_id")(self.deps['metadata'])

        _id = uuid.UUID(_id)

        collection = self.connection[doc]

        found = collection.find_one_and_update({'id': _id}, {'$set': {f"{doc_path}": _id}})

        if not found:
            raise KeyError(f"Expected {doc} Document id:{doc_id}, but found none.")

    def rollback(self) -> None:
        """No Rollback."""
        pass
