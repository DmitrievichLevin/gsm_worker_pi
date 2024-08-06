"""Metadata Delete Module"""
from __future__ import annotations

import logging
import os
from typing import Any

import pymssql

from ..sync_sub import SubProcess


class MetaDelete(SubProcess):
    """Delete MetaData SubProcess"""

    # Successfully deleted object ID(s)
    deleted: list[str]

    # SQL Attrs
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

    def execute(self) -> None:
        """Execute SQL Stored Procedure"""
        # Initialize Queue for Response
        del_id = self.deps['del_queue']

        with self.cursor as cursor:
            cursor.callproc("deleteMedia", (del_id,))

            new_row, *_ = cursor

            self.connection.commit()

            # Set result property
            self.deps['deleted'] = del_id

            # Log delete
            logging.info("Deleted Media Record ID: %s", new_row)

    def rollback(self) -> None:
        """Rollback SQL Commands"""
        self.connection.rollback()
