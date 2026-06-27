# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
from scraping_ebay.items import EbayItem

class EbayTestSpider(scrapy.Spider):
    name = 'ebay-test'
    allowed_domains = ["www.ebay.com"]

    start_urls = [
        "https://www.ebay.com/sch/i.html?_nkw=laptop"
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 4,
        "RETRY_TIMES": 3,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "HTTPERROR_ALLOW_ALL": True,
    }

    def parse(self, response):
        items = response.css(".s-item")

        for item in items:

            title = item.css(".s-item__title::text").extract_first()
            price = item.css(".s-item__price::text").extract_first()
            shipping = item.css(".s-item__shipping::text").extract_first()
            location = item.css(".s-item__location::text").extract_first()
            link = item.css(".s-item__link::attr(href)").extract_first()

            # Skip ads / empty tiles
            if not title or "Shop on eBay" in title:
                continue

            # Clean URL
            if link:
                link = urljoin(response.url, link.split("?")[0])

            yield EbayItem(
                title=title.strip() if title else None,
                price=price.strip() if price else None,
                shipping=shipping.strip() if shipping else None,
                location=location.strip() if location else None,
                item_url=link
            )

        # ----------------------------
        # Pagination (SAFE VERSION)
        # ----------------------------

        next_page = response.css(
            "a.pagination__next::attr(href)"
        ).extract_first()
        if next_page:
            yield scrapy.Request(
                urljoin(response.url, next_page),
                callback=self.parse,
                dont_filter=True
            )
