"""Media Deserializer"""

import sys
import base64
import uuid
from io import BytesIO
from typing import Any, Callable, Generator, Generic, TypeVar, Union
import multipart as mp
from PIL import Image as Pil, ImageFile
import pillow_heif
import filetype as ft

BASE: int = 1800
THUMB: int = 500

Image = Union[Pil.Image, ImageFile.ImageFile]
MediaProp = TypeVar("MediaProp", bound=str)
LambdaEvent = dict[str, Any]


class Media(Generic[MediaProp]):
    """Media Deserializer

    - Parses multipart form media file

    Raises:
        TypeError: Unsupported file type
        TypeError: Invalid content-type, expected multipart/form-data

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """
    id: uuid.UUID
    format: MediaProp
    user: MediaProp
    # ----Files----
    image: bytes
    thumbnail: bytes
    # -------------

    # -File Size (b)-
    image_size: int
    thumbnail_size: int
    # ---------------

    length: int = 0
    allowed_extensions: dict[Any, Any] = {
        'jpeg': 'jpg',
        'png': 'png',
        # Convert HEIC to JPEG
        'heic': 'jpg'
    }

    def __init__(self, event: LambdaEvent):
        headers = event["headers"]
        cont_type = headers["content-type"]
        cont_len = len(event["body"])

        self.__parse(cont_type, cont_len, event["body"])

    @property
    def file_sizes(self) -> tuple[int, int]:
        """Media File Sizes

        Returns:
            tuple[int, int]: media & thumbnail size in bytes.
        """
        return self.image_size, self.thumbnail_size

    def __parse(self, _type: str, _len: int, body_str: str) -> None:
        """Parse Multipart File Upload

        Args:
            _type (str): content-type header
            _len (int): length of body
            body (str): body
        """

        body = BytesIO(base64.b64decode(body_str))

        # Get Boundary & size
        boundary, memfile_limit = self._pdict(_type, _len)

        multipart = mp.MultipartParser(body, boundary, memfile_limit)

        raw = BytesIO(multipart.get("file")[0])

        user_id = multipart.get("id")[0]

        self.id = uuid.uuid4()

        self.user = user_id

        mime, extension = (lambda x: [None, None] if x is None else x.split("/"))(
            ft.guess_mime(raw)
        )

        match mime:
            case "image":
                self._process_img(raw, extension)
            case _:
                raise TypeError(
                    f"Expected image, but found {mime}."
                )

    def _process_img(self, bts: BytesIO, extension: MediaProp) -> None:

        # For HEIC
        pillow_heif.register_heif_opener()

        img: Any = Pil.open(bts)

        try:
            self.format = self.allowed_extensions[extension]
        except Exception:
            raise TypeError(
                f"File extension not supported {extension}"
            )

        # Resize Image to correct dimensions if applicable
        if img.width > BASE or img.height > BASE:
            img = self._resize(img)

        full_img = BytesIO()
        thumb_img = BytesIO()

        img.save(full_img, format=self.format)

        thumbnail = self.__thumbnail(img)
        thumbnail.save(thumb_img, format=self.format)

        thumbnail.close()

        full_img.seek(0)
        thumb_img.seek(0)

        i_by = full_img.getvalue()
        t_by = thumb_img.getvalue()

        self.image = i_by
        self.image_size = sys.getsizeof(i_by)

        self.thumbnail = t_by
        self.thumbnail_size = sys.getsizeof(t_by)

    def __thumbnail(self, pil_img: Image) -> Image:
        img_width, img_height = pil_img.size
        return pil_img.crop(
            (
                (img_width - 200) // 2,
                (img_height - 200) // 2,
                (img_width + 200) // 2,
                (img_height + 200) // 2,
            )
        )

    def __iter__(
        self,
    ) -> Generator[MediaProp | int | uuid.UUID, None, None]:
        """Dunder Overwrite

        Yields:
            Generator[MediaProp | int | uuid.UUID, None, None]: _description_
        """
        properties: list[MediaProp | int | uuid.UUID] = [
            self.id, self.user, self.format, self.length]
        for value in properties:
            yield value

    @classmethod
    def _resize(cls, image: ImageFile.ImageFile) -> Image:
        pct: Callable[[int, float | int], int] = lambda key, x: int(float(image.size[key]) * (
            BASE / float(x)
        ))

        new_size: tuple[int, int] = (
            (BASE, pct(0, image.height))
            if image.width > BASE
            else (pct(1, image.width), BASE)
        )

        resized_image = image.resize(
            new_size, Pil.Resampling.NEAREST
        )

        image.close()
        return resized_image

    def _pdict(
        self, _type: str, _len: int
    ) -> tuple[MediaProp, int]:
        ctype, pdict = mp.parse_options_header(_type)

        boundary: MediaProp = pdict["boundary"]

        if ctype != "multipart/form-data":
            raise TypeError(
                f"Expected multipart/form-data, but found {ctype}"
            )
        else:
            return boundary, _len