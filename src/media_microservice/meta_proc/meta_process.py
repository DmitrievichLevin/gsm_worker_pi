"""MetaProcess Module"""
from __future__ import annotations

import logging
import os
from typing import Any

import pymssql

from ..sync_sub import SubProcess


class MetaProcess(SubProcess):
    """Insert New Media metadata Row"""
    cursor: pymssql.Cursor
    connection: pymssql.Connection

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)
        # Connect to SQL
        # pylint: disable=no-member
        host = os.environ.get("sql_host")
        uname = os.environ.get("sql_uname")
        pword = os.environ.get("sql_pword")
        db = os.environ.get("sql_db")
        _connection = pymssql.connect(host, uname, pword, db)
        self.connection = _connection
        self.cursor = _connection.cursor(as_dict=True)

    @property
    def meta_row(self) -> tuple[str, str, str, str, str, str, str, str, int, int]:
        """Create Metadata Procedure Params

        Returns:
            tuple[str, str, str, str, str, str, str, str, int]: SQL Procedure params
        """
        media_id = self.deps["id"]
        user_id = self.deps["owner"]
        bucket = self.deps["bucket"]
        doc = self.deps["doc"]
        doc_id = self.deps["doc_id"]
        doc_path = self.deps["doc_path"]
        mime = self.deps["mime"]
        file_ext = self.deps["file_ext"]
        file_size = self.deps["file_size"]
        thumb_size = self.deps["thumb_size"]

        return (
            media_id,
            user_id,
            bucket,
            doc,
            doc_id,
            doc_path,
            mime,
            file_ext,
            file_size,
            thumb_size,
        )

    def execute(self) -> None:
        """Execute SQL Stored Procedure"""
        with self.cursor as cursor:
            cursor.callproc("createMeta", self.meta_row)

            new_row, *_ = cursor
            logging.info("Created Media Record:\nmetadata: %s", new_row)
            # Update deps for next SubProcess
            self.deps["metadata"] = new_row

            self.connection.commit()

    def rollback(self) -> None:
        """Rollback SQL Commands"""
        self.connection.rollback()
