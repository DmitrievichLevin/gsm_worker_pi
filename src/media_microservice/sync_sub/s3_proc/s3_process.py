"""S3 Media SubProcess"""
from __future__ import annotations
import os
from typing import Any
import boto3
from mypy_boto3_s3 import S3Client
from media_microservice.media import Media
from media_microservice.sync_sub import SubProcess


s3: S3Client = boto3.client("s3")


class S3_Process(SubProcess):
    """AWS S3 Media Upload Process"""
    bucket: str = os.environ['AWS_BUCKET'] or "bevor-dev"
    completed: list[str] = []

    def __init__(self, event: dict[str, Any], deps: dict[str, Any]) -> None:
        super().__init__(event, deps)
        self.deps['media'] = Media(event)

    @property
    def sub_dir(self) -> str:
        """Bucket Sub-directory

        Returns:
            str: sub-directory
        """
        return f"{self.deps['owner']}/{self.deps['id']}/"

    @property
    def img_name(self) -> str:
        """Image Filename

        Returns:
            str: file-name
        """
        return f"{self.deps['id']}-image"

    @property
    def thumb_name(self) -> str:
        """Thumbnail Filename

        Returns:
            str: file-name
        """
        return f"{self.deps['id']}-thumb"

    @property
    def media(self) -> Media[Any]:
        """Media Instance

        Returns:
            str: file-name
        """
        _media: Media[Any] = self.deps['media']
        return _media

    def __filename(self, name: str, ext: str) -> str:
        """Concat Name & Extension"""
        return name + "." + ext

    def bucket_args(self, media: Media[Any]) -> tuple[tuple[str, str, bytes], tuple[str, str, bytes]]:
        """S3 Client Method Args

        Args:
            media (Media[Any]): Media instance

        Raises:
            TypeError: Cannot determine media/image format.

        Returns:
            tuple[tuple[str,str, bytes], tuple[str, str, bytes]]: image | thumbnail, key, & bytes tuples
        """
        _format = media.format

        self.deps['file_ext'] = _format

        if _format is None:
            raise TypeError("Cannot determine media/image format.")

        return ('image', self.__filename(self.sub_dir + self.img_name, _format), media.image), ('thumb', self.__filename(self.sub_dir + self.thumb_name, _format), media.thumbnail)

    def presigned_url_get(self, key: str) -> str:
        """Generate Pre-Signed-Url for Media File

        Args:
            key (str): S3 key

        Raises:
            RuntimeError: Unable to generate url.

        Returns:
            str: presigned-url
        """
        response = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket,
                'Key': key,
            }, ExpiresIn=3600)

        if response is None:
            raise RuntimeError("Unable to generate pre-signed url.")

        return response

    def execute(self) -> None:
        _media = self.media

        _args = self.bucket_args(_media)

        for field, k, b in _args:
            s3.put_object(Bucket=self.bucket, Key=k, Body=b)

            # Update deps w/ presigned url of newly added media
            self.deps[field + '_url'] = self.presigned_url_get(k)

            # Track completed
            self.completed.append(k)

        # Update deps for next Process(Meta_SQL)
        file_size, thumb_size = self.deps['media'].file_sizes

        self.deps['bucket'] = self.bucket
        self.deps['file_size'] = file_size
        self.deps['thumb_size'] = thumb_size

        # Empty completed on success
        self.completed = []

    def rollback(self) -> None:
        for k in self.completed:
            try:
                s3.delete_object(Bucket=self.bucket, Key=k)
            except Exception:
                pass
