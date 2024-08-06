"""S3 Subprocess Module"""
from .s3_delete import S3Delete
from .s3_process import S3Process

__all__ = ["S3Process", "S3Delete"]
