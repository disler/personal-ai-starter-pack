from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union

import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2:")
warnings.filterwarnings(
    "ignore", message='Field "model_id" has conflict with protected namespace "model_".'
)


class Interaction(BaseModel):
    role: str
    content: str


from enum import Enum


class ImageRatio(str, Enum):
    SQUARE = "1024x1024"
    PORTRAIT = "1024x1792"
    LANDSCAPE = "1792x1024"


class Style(str, Enum):
    VIVID = "vivid"
    NATURAL = "natural"


class Quality(str, Enum):
    STANDARD = "standard"
    HD = "hd"


class GenerateImageParams(BaseModel):
    prompts: List[str]
    quality: Quality
    image_ratio: Optional[ImageRatio]
    style: Optional[Style]


class ImageFormat(str, Enum):
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"


class ConvertImageParams(BaseModel):
    version_numbers: List[int]
    image_format: ImageFormat

class ResizeImageParams(BaseModel):
    version_numbers: List[int]
    width: int
    height: int

class OpenImageDirParams(BaseModel):
    pass
