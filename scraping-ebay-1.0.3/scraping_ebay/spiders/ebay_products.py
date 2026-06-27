import scrapy
import argparse
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse

class EbayProductsSpider(scrapy.Spider):
    name = "ebay-products"
    allowed_domains = ["ebay.com"]
    start_urls = ["https://ebay.com"]

    def __init__(self, search_query="laptop", pages=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_query = search_query
        self.pages = max(1, int(pages))
        self.base_url = "https://www.ebay.com/sch/i.html"

    async def start(self):
        yield self.homepage_request()
    
    def homepage_request(self):
        return scrapy.Request(
            "https://www.ebay.com/",
            callback=self.start_search_pages,
            dont_filter=True,
        )
    def start_search_pages(self, response):
        if response.status == 403:
            self.logger.warning("Homepage returned 403; trying search pages anyway.")

        for page in range(1, self.pages + 1):
            params = {
                "_nkw": self.search_query,
                "_sacat": "0",
                "_pgn": page,
            }
            url = f"{self.base_url}?{urlencode(params)}"
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"page": page},
                headers={"Referer": response.url},
            )

    def parse(self, response):
        if response.status == 403:
            self.logger.warning("Search page %s returned 403: %s", response.meta["page"], response.url)
            return

        cards = response.css("li.s-item, li.s-card")

        for position, card in enumerate(cards, start=1):
            lines = self.text_lines(card)
            title = self.first_value(
                card,
                [
                    ".s-item__title::text",
                    ".s-card__title ::text",
                    ".s-card__image::attr(alt)",
                ],
            )

            # eBay usually includes one placeholder result card at the top.
            if not title or title.lower() == "shop on ebay":
                continue

            item_url = self.first_value(
                card,
                [
                    ".su-card-container__header .s-card__link::attr(href)",
                    ".s-item__link::attr(href)",
                    ".s-card__link::attr(href)",
                ],
            )
            image_url = self.first_value(
                card,
                [
                    ".s-item__image-wrapper img::attr(src)",
                    ".s-item__image-wrapper img::attr(data-src)",
                    ".s-card__image::attr(src)",
                    ".s-card__image::attr(data-defer-load)",
                ],
            )
            product_id = self.product_id(card, item_url)

            yield {
                "search_query": self.search_query,
                "page": response.meta["page"],
                "position": position,
                "product_id": product_id,
                "title": title,
                "price": self.first_value(
                    card,
                    [
                        ".s-item__price::text",
                        ".s-card__price::text",
                    ],
                ),
                "condition": self.first_value(
                    card,
                    [
                        ".SECONDARY_INFO::text",
                        ".s-card__subtitle .su-styled-text::text",
                        ".s-card__subtitle::text",
                    ],
                ),
                "shipping": self.first_value(
                    card,
                    [
                        ".s-item__shipping::text",
                        ".s-item__logisticsCost::text",
                    ],
                )
                or self.find_line(lines, ["shipping", "delivery", "postage"]),
                "location": self.first_value(card, [".s-item__location::text"])
                or self.find_line(lines, ["located in", "from "]),
                "seller": self.first_value(card, [".s-item__seller-info-text::text"])
                or self.extract_seller(lines),
                "item_url": item_url,
                "image_url": image_url,
                "image_path": self.image_path(product_id, image_url),
            }
    def first_value(self, selector, css_selectors):
        for css_selector in css_selectors:
            value = self.clean(selector.css(css_selector).get())
            if value:
                return value
        return None

    def text_lines(self, selector):
        lines = []
        for value in selector.css("::text").getall():
            value = self.clean(value)
            if value:
                lines.append(value)
        return lines

    def find_line(self, lines, keywords):
        for line in lines:
            lowered = line.lower()
            if any(keyword in lowered for keyword in keywords):
                return line
        return None

    def extract_seller(self, lines):
        ignored = ("sold", "sponsored", "refurbished", "delivery", "located in")

        for index, line in enumerate(lines):
            if "positive" not in line.lower() or index == 0:
                continue

            candidate = lines[index - 1]
            if not any(word in candidate.lower() for word in ignored):
                return candidate

        return None

    def product_id(self, card, item_url):
        product_id = self.clean(card.attrib.get("data-listingid"))
        if product_id and product_id.isdigit():
            return product_id

        if item_url:
            match = re.search(r"/itm/(?:[^/?#]+/)?(\d+)", item_url)
            if match:
                return match.group(1)

        return None
    
    def image_path(self, product_id, image_url):
        if not product_id or not image_url:
            return None

        extension = self.extension_from_url(image_url)
        return f"{product_id}{extension}"
    
    def extension_from_url(self,url):
        suffix = Path(urlparse(url).path).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            return suffix
        return ".jpg"

    @staticmethod
    def clean(value):
        if value is None:
            return None
        return " ".join(value.split()).strip(" ·")
