from .base_extractor import BaseExtractor
from models.summary_product import SummaryProduct
from utils.selectors import SelectorUtils
from utils.url_utils import URLUtils

class SearchPageExtractor(BaseExtractor):

    def __init__(self,product_node):
        self.node = product_node
    
    def extract(self):

        product_url = self._extract_product_url()
        
        if not product_url:
            return None
        product_id = URLUtils.extract_product_id(url=product_url)
        
        return SummaryProduct(
            product_id=product_id,
            product_url=product_url,
            title=self._extract_title(),
            price=self._extract_price(),
            condition=self._extract_condition(),
            shipping=self._extract_shipping(),
            location=self._extract_location(),
            image_url=self._extract_image_url(),
        )
    # ------------------------------------------------------------------
    # Private helper methods
    # ------------------------------------------------------------------

    def _text(self,selector,default=None):
        return SelectorUtils.css_text(node=self.node,selector=selector,default=default)
    
    def _attr(self,selector,default=None):
        return SelectorUtils.css_attr(node=self.node,selector=selector,default=default)
    
    # ------------------------------------------------------------------
    # Individual field extractors
    # ------------------------------------------------------------------
    
    def _extract_product_url(self):
        return self._attr("a.s-card__link::attr(href)")

    def _extract_product_id(self):
        pass

    def _extract_title(self):
        return self._text(".s-card__title > span:first-child::text")

    def _extract_price(self):
        return self._text(".s-card__price::text")

    def _extract_condition(self):
        condition = self._text(
            ".s-card__subtitle span:first-child::text"
        )

        if condition:
            condition = condition.replace("·", "").strip()

        return condition


    def _extract_shipping(self):
        for row in self.node.css(".s-card__attribute-row"):

            text = " ".join(
                t.strip()
                for t in row.css("span::text").getall()
                if t.strip()
            )

            if "delivery" in text.lower():
                return text

        return None

    def _extract_location(self):
        for row in self.node.css(".s-card__attribute-row"):

            text = " ".join(
                t.strip()
                for t in row.css("span::text").getall()
                if t.strip()
            )

            if text.startswith("Located"):
                return (
                    text
                    .replace("Located in", "")
                    .strip()
                )

        return None

    def _extract_image_url(self):
        return self._attr(
            "img.s-card__image::attr(src)"
        )