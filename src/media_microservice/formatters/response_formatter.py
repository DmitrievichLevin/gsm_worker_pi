"""Response Formatter"""
from __future__ import annotations

import time
from abc import ABCMeta
from abc import abstractmethod
from operator import itemgetter
from typing import Any


class ResponseFormatter(metaclass=ABCMeta):
    """Abstract Response Formatter"""

    @classmethod
    @abstractmethod
    def format(cls, result: dict[str, Any]) -> dict[str, Any]:
        """Format Response"""
        raise NotImplementedError


class MediaResponse(ResponseFormatter):
    """Reshape Media Response."""
    @classmethod
    def format(cls, result: dict[str, Any]) -> dict[str, Any]:
        """Format Response Body"""
        raw_meta = result['metadata']

        _id, doc, doc_id, doc_path, mime, file_ext, file_size, owner, created_at = itemgetter(
            "id", "doc", "doc_id", "doc_path", "mime", "file_ext", "file_size", "owner", "created_at")(raw_meta)

        return dict(id=_id, url=result['image_url'], thumbnail=result['thumb_url'], metadata=dict(
            parent=doc, owner=owner, parentId=doc_id, path=doc_path, mime=mime, type=file_ext, created_at=created_at, size=file_size))


class DocumentResponse(ResponseFormatter):
    """Format Document Response"""

    @classmethod
    def format(cls, result: dict[str, Any]) -> dict[str, Any]:
        """Document Response Formatter

        Args:
            result (dict[str, Any]): SyncProcess response.

        Returns:
            dict[str, Any]: HTTP response body.
        """
        response: dict[str, Any] = {}

        response.update(**result)

        _id = str(response.pop('_id'))

        created_at = time.mktime(response.pop('created_at').timetuple())

        updated_at = time.mktime(response.pop('updatedAt').timetuple())

        response.pop("__v")

        response.update(id=_id, created_at=created_at, updatedAt=updated_at)

        return response
