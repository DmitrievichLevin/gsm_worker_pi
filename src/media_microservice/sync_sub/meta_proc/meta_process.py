from __future__ import annotations
import os
from typing import Any
import pymssql
from media_microservice.sync_sub import SubProcess


class Meta_Process(SubProcess):
    """Insert New Media metadata Row"""
    host = os.environ["sql_host"] or "bevor-server.database.windows.net"
    uname = os.environ["sql_uname"] or "bevor_dev"
    pword = os.environ["sql_pword"] or "minuteRice@1234$"
    db = os.environ["sql_db"] or "bevor_dir"
    cursor: pymssql.Cursor
    connection: pymssql.Connection

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)
        # Connect to SQL
        # pylint: disable=no-member
        _connection = pymssql.connect(
            self.host, self.uname, self.pword, self.db)
        self.connection = _connection
        self.cursor = _connection.cursor(as_dict=True)

    @property
    def meta_row(self) -> tuple[str, str, str, str, str, str, int, int]:
        """Create Metadata Procedure Params

        Returns:
            tuple[str, str, str, str, str, str, int]: SQL Procedure params
        """
        media_id = self.deps['id']
        user_id = self.deps['owner']
        bucket = self.deps['bucket']
        doc = self.deps['doc']
        doc_path = self.deps['doc_path']
        file_ext = self.deps['file_ext']
        file_size = self.deps['file_size']
        thumb_size = self.deps['thumb_size']

        return (media_id, user_id, bucket, doc, doc_path, file_ext, file_size, thumb_size)

    def execute(self) -> None:
        cursor = self.cursor
        with cursor:
            cursor.callproc('media.createMeta', self.meta_row)

            newRow, *_ = cursor

            # Update deps for next SubProcess
            self.deps['metadata'] = newRow

    def rollback(self) -> None:
        self.connection.rollback()
