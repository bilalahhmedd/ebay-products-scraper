from typing import Optional
from .base import BaseEntity

class Image(BaseEntity):
    """
    Represents one product image
    """
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[int] = None
    is_primary: bool = False
