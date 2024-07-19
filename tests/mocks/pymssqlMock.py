"""Pymssqlmock"""
from typing import Any
from typing import Iterator


class BogusSQL:
    """Mock Pymssql"""
    inserted = {'id': 'b292a405-446e-4720-bdb6-292288459f53', 'owner': '123-456', 'doc': 'User', 'doc_id': 'u34-4675',
                'doc_path': 'profileImage', 'file_ext': 'jpeg', 'file_size': 32813, 'thumb_size': 8780, 'created_at': 1721419334}

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        """Mock pymssql.connect(arg)"""
        pass

    def cursor(self, *_args: Any, **_kwargs: Any) -> Any:
        """Mock pymssql.cursor(arg)"""
        return self

    def callproc(self, *_args: Any, **_kwargs: Any) -> None:
        """Mock Call Procedure"""
        pass

    def commit(self, *_args: Any, **_kwargs: Any) -> None:
        """Mock Commit"""
        pass

    def rollback(self, *_args: Any, **_kwargs: Any) -> None:
        """Mock Rollback"""
        pass

    def __enter__(self, *_args: Any, **_kwargs: Any) -> Any:
        """Mock __enter__"""
        return self

    def __exit__(self, *_args: Any, **_kwargs: Any) -> Any:
        """Mock __exit__"""
        pass

    def __iter__(self) -> Iterator[Any]:
        return iter([self.inserted, None])
