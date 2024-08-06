"""S3 Delete SubProcess"""
import logging
import os
from typing import Any
from typing import Sequence

import boto3
from mypy_boto3_s3 import S3Client
from urllib3.exceptions import HTTPError

from ..sync_sub import SubProcess


class S3Delete(SubProcess):
    """Delete File From Bucket"""

    # AWS Attrs
    bucket: str
    s3: S3Client

    # User Id Query Param
    user: str
    # Object Id Query Param
    id: str
    # Object Document Name Query Param
    doc: str
    # Object Document Id Query Param
    doc_id: str
    # Object Document Path Query Param
    doc_path: str

    # Result
    deps: dict[str, Any]

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)

        # Initialize Bucket
        self.bucket = os.environ.get("AWS_BUCKET") or "bevor-dev"
        self.s3: S3Client = boto3.client("s3")

        # Initialize queue for next process(SQL)
        self.deps['del_queue'] = None

        query = event.get("queryStringParameters", {})

        try:
            # Attempt to extract query params
            self.user = query.get("user_id")
            self.id = query.get("id")
            self.doc = query.get("doc")
            self.doc_id = query.get("doc_id")
            self.doc_path = query.get("doc_path")

            # Update Deps for next Process(s)
            self.deps.update(user=self.user, doc=self.doc, doc_id=self.doc_id, doc_path=self.doc_path)

        except Exception as e:
            _err = "Missing required query params expected user_id, id(mediaId), doc_id, & doc_path %s" % e
            logging.warning(_err)
            raise KeyError(_err) from e

    def _on_delete(self, key: str) -> None:
        """S3 Delete Callback

        - Save successfully deleted ID's for metadata delete

        Args:
            key (str): key of deleted Item.
        """
        self.deps['del_queue'] = key

    def execute(self) -> None:
        """Execute S3 Delete Object"""
        try:
            # Get contents of directory
            contents = self.s3.list_objects(Bucket=self.bucket, Prefix=f"{self.user}/{self.id}")['Contents']

            keys: Sequence[Any] = [{"Key": content['Key']} for content in contents]

            # Attempt to delete Objects
            self.s3.delete_objects(Bucket=self.bucket, Delete={'Objects': keys})

            # Store keys for meta delete
            self._on_delete(self.id)

        except Exception as e:
            _err = "Unable to delete S3 Object(s) Prefix Id:%s \nCause:%s" % (f"{self.user}/{self.id}", e)

            # Log delete fail for manual data cleanup
            logging.error(_err)
            raise HTTPError(_err) from e

    def rollback(self) -> None:
        """No Rollback S3 Delete"""
        pass
