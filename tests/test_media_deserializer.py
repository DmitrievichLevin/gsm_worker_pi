"""Test Media Deserializer"""
# pylint: disable=unused-import
# pylint: disable=import-error
# mypy: ignore-errors
from typing import Generic
from typing import TypeVar

import pytest

from .lamb_data import TEvent
from media_microservice import LambdaEvent
from media_microservice import Media
from media_microservice import MetaProcess
from media_microservice import S3Process
from media_microservice import Sync


def test_media_deserializer_jpeg() -> None:
    """Test Place Holder"""
    t = Media(TEvent)
    raise Exception()
    assert t.format == "jpeg"
