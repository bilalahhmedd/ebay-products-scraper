from decimal import Decimal
from typing import Optional

from .base import BaseEntity

class SummaryProduct(BaseEntity):
    """
    Product information available
    from search product page
    """

    product_id: str
    product_url: str

    title: str
    price: Optional[str] = None
    currency: Optional[str] = None
    condition: Optional[str] = None
    shipping: Optional[str] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    marketplace: str = "ebay"