from typing import Dict
from typing import List
from typing import Optional
from pydantic import Field

from .image import Image
from .summary_product import SummaryProduct


class Product(SummaryProduct):
    """
    Complete Product Information
    """
    brand: Optional[str] = None

    upc: Optional[str] = None

    mpn: Optional[str] = None

    model: Optional[str] = None

    description: Optional[str] = None

    seller: Optional[str] = None

    item_specifics: Dict[str, str] = Field(default_factory=dict)

    images: List[Image] = Field(default_factory=list)