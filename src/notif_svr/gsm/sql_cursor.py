"""SQL Cursor Module."""

import os
from typing import Any, Callable, TypedDict
import pymssql


class ICursor(TypedDict):
    callproc: Callable[[str, dict[str, Any]], None]


class ISQLCon(TypedDict):
    cursor: Callable[..., Any]


class SQLCursor:
    sql: ISQLCon

    def __init__(self, *__args: tuple[Any, ...], **__kwargs: dict[str, Any]) -> None:
        # SQL
        host = os.environ.get("sql_host")
        uname = os.environ.get("sql_uname")
        pword = os.environ.get("sql_pword")
        db = os.environ.get("sql_db")
        # pylint: disable=no-member
        self.sql = pymssql.connect(host, uname, pword, db)
