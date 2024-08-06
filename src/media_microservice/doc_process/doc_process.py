"""Mongo Document SubProcess"""
from __future__ import annotations

import logging
import os
from operator import itemgetter
from typing import Any

import bson
import pymongo

from ..sync_sub import SubProcess


class DocumentProcess(SubProcess):
    """Attach/Remove Uploaded Media to Parent Document"""
    connection: Any

    # Mongo Document before update
    original: Any

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)
        uri = os.environ.get("MONGO_URI")
        db_name = os.environ.get("MONGO_DB_NAME")
        self.connection = pymongo.MongoClient(uri, uuidRepresentation="standard").get_database(db_name)

    @property
    def __get_metadata(self) -> tuple[str, str, str, bson.ObjectId]:
        """Get Media Metadata

        - Attempt extracting deps.metadata, then queryStringParameters for document properties.

        Returns:
            media_meta(tuple[str | None, str, str, bson.ObjectId]): document media metadata, _id is None for delete's.

        Raises:
            KeyError: Unable to extract metadata for process.
        """
        # If delete Req return _id = None
        is_del = self.event["requestContext"]["http"]["method"] == "DELETE"

        try:
            _meta = self.deps.get('metadata', self.event.get("queryStringParameters", None))

            _id, doc, doc_path, doc_id = itemgetter("id", "doc", "doc_path", "doc_id")(_meta)

            return _id if not is_del else None, doc, doc_path, doc_id
        except Exception as e:
            raise KeyError("Expected metadata/query-params expected user_id, id(mediaId), doc, doc_id, & doc_path, but missing %s." % e) from e

    def execute(self) -> None:
        """Parent Document Update

        Raises:
            KeyError: Parent Document doesn't exist
        """
        _id, doc, doc_path, doc_id = self.__get_metadata

        # str->ObjectId
        doc_id = bson.ObjectId(doc_id)

        found = self.connection[doc + 's'].find_one({'_id': doc_id})

        self.original = found

        if not found:
            raise KeyError(f"Expected {doc} Document id:{doc_id}, but found none.")

        # Add 's' to document_name for collection_name
        found = self.connection[doc + 's'].find_one_and_update(
            {'_id': doc_id}, {'$set': {f"{doc_path}": _id}}, return_document=pymongo.ReturnDocument.AFTER)

        # Add updated document to result
        self.deps['updated_doc'] = found

    def rollback(self) -> None:
        """No Rollback."""
        # Available METHODS GET, DELETE
        method = self.event["requestContext"]["http"]["method"]

        # Log Rollback
        _logwrng = "Rolling back document update method:%s\ndocument:%s" % (method, self.original)
        logging.warning(_logwrng)

        match(method):
            case 'DELETE':
                try:
                    if self.original:
                        _id, doc, doc_path, doc_id = self.__get_metadata

                        # str->ObjectId
                        doc_id = bson.ObjectId(doc_id)

                        paths = doc_path.split(".")

                        pointer = self.original

                        # Traverse path for updated property
                        for p in paths:
                            pointer = pointer[p]

                        # Rollback Document update
                        self.connection[doc + 's'].find_one_and_update(
                            {'_id': doc_id}, {'$set': {f"{doc_path}": pointer}}, return_document=pymongo.ReturnDocument.AFTER)
                except Exception as e:
                    _logmsg = "Failed to revert document on rollback Exception:%s\nDocument:%s" % (e, self.original)
                    logging.error(_logmsg)
            case _:
                pass
