from typing import Dict
from typing import List
from typing import Optional
from pydantic import Field

from .image import Image
from .summary_product import SummaryProduct


class Product(SummaryProduct):
    """
    Complete product information extracted from the product detail page.
    """

    # -----------------------------
    # Product Attributes
    # -----------------------------
    brand: Optional[str] = None
    department: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    model: Optional[str] = None
    mpn: Optional[str] = None
    upc: Optional[str] = None

    # -----------------------------
    # Product Description
    # -----------------------------
    description: Optional[str] = None

    # -----------------------------
    # Seller Information
    # -----------------------------
    seller_name: Optional[str] = None
    seller_feedback: Optional[str] = None
    seller_rating: Optional[str] = None

    # -----------------------------
    # Shipping / Returns
    # -----------------------------
    shipping_cost: Optional[str] = None
    shipping_service: Optional[str] = None
    estimated_delivery: Optional[str] = None
    returns: Optional[str] = None

    # -----------------------------
    # Item Specifics
    # -----------------------------
    item_specifics: dict[str, str] = Field(default_factory=dict)

    # -----------------------------
    # Images
    # -----------------------------
    image_urls: list[str] = Field(default_factory=list)

    images: list[Image] = Field(default_factory=list)