from typing import Optional

from scraping_ebay.extractors.base_extractor import BaseExtractor
from scraping_ebay.models.product import Product
from scraping_ebay.models.summary_product import SummaryProduct
from scraping_ebay.utils.image_utils import ImageUtils

def ProductPageExtractor(BaseExtractor):

    def __init__(self,response,summary: SummaryProduct):
        self.response = response
        self.summary = summary
    

    def extract(self) -> Product:
        
        item_specifics = self._extract_item_specifics()
        
        return Product(
            #-----------------------------------
            # summary product items
            #-----------------------------------
            product_id=self.summary.product_id,
            product_url=self.summary.product_url,
            title=self.summary.title,
            price=self.summary.price,
            currency=self.summary.currency,
            condition=self.summary.condition,
            shipping=self.summary.shipping,
            location=self.summary.location,
            image_url=self.summary.image_url,
            marketplace=self.summary.marketplace,
            #-----------------------------------
            # extracted item specs
            #-----------------------------------
            brand=item_specifics.get("Brand"),
            department=item_specifics.get("Department"),
            color=item_specifics.get("Color")
            size=(
                item_specifics.get("US Shoe Size")
                or item_specifics.get("Size")
            ),
            upc=item_specifics.get("UPC"),
            mpn=item_specifics.get("MPN"),
            model=item_specifics.get("Model"),

            item_specifics=item_specifics,
            image_urls=self._extract_gallery_images(),

        )

    def _extract_gallery_images(self):
        
        image_urls = []
        gallery = self.response.css("div.ux-image-carousel img")
        for img in gallery:

            url = (
                img.css("::attr(data-zoom-src)").get()
                or img.css("::attr(src)").get()
                or img.css("::attr(data-src)").get()
            )
            url = ImageUtils.get_high_resolution_url(url)
            
            if not url:
                continue
            if "i.ebayimg.com" not in url:
                continue

            image_urls.append(url)

        return list(dict.fromkeys(image_urls))
    
    def _extract_item_specifics(self):
        section = self.response.css(
            "div[data-testid='x-about-this-item']"
        )

        return self._extract_specs(section)

    def _extract_specs(self,section):
        specs = {}

        rows = section.css("div.ux-layout-section__row")

        for row in rows:

            label = "".join(
                row.css(
                    ".ux-labels-values__labels ::text"
                ).getall()
            ).strip()

            value = " ".join(
                t.strip()
                for t in row.css(
                    ".ux-labels-values__values ::text"
                ).getall()
                if t.strip()
            )

            if label and value:
                specs[label] = value

        return specs
