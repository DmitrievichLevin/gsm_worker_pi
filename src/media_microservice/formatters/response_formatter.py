"""Response Formatter"""
from __future__ import annotations

from operator import itemgetter
from typing import Any


class MediaResponse():
    """Reshape Media Response."""
    @classmethod
    def format(cls, result: dict[str, Any]) -> dict[str, Any]:
        """Format Response Body"""
        raw_meta = result['metadata']

        _id, doc, doc_id, doc_path, file_ext, file_size, owner, created_at = itemgetter(
            "id", "doc", "doc_id", "doc_path", "file_ext", "file_size", "owner", "created_at")(raw_meta)

        return dict(id=_id, url=result['image_url'], thumbnail=result['thumb_url'], metadata=dict(
            parent=doc, owner=owner, parentId=doc_id, path=doc_path, type=file_ext, created_at=created_at, size=file_size))
