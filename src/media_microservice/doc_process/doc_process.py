"""Mongo Document SubProcess"""
from __future__ import annotations

import os
from operator import itemgetter
from typing import Any

from mongoengine import connect
from mongoengine import Document

from ..sync_sub import SubProcess

os.environ['MONGO_URI'] = "mongodb+srv://bev-dev:MPndTl0nQjPL7a4z@bevor-dev.uma4aiv.mongodb.net/?retryWrites=true&w=majority&appName=bevor-dev"


class DocumentProcess(SubProcess):
    """Attach Uploaded Media to Parent Document"""

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)
        uri = os.environ.get("MONGO_URI")
        self.connection = connect(host=uri)

    def execute(self) -> None:
        """Parent Document Update

        Raises:
            KeyError: Parent Document doesn't exist
        """
        _id, doc, doc_path, doc_id = itemgetter("id", "doc", "doc_path", "doc_id")(self.deps['metadata'])

        document: Document = self.connection[doc]

        with document.objects(id=doc_id) as found:
            print("track found", found)
            if not found:
                raise KeyError(f"Expected {doc} Document id:{doc_id}, but found none.")

            found.update(__raw__={'$set': {f"{doc_path}": _id}})

    def rollback(self) -> None:
        """No Rollback."""
        pass
