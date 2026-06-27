# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http.request import Request
from scrapy.pipelines.files import FilesPipeline

from pathlib import Path
from urllib.parse import urlencode, urlparse
from logging import INFO


class EbayProductImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        image_url = item.get("image_url")
        product_id = item.get("product_id")

        if not image_url or not product_id:
            info.log('\n Invalid image URL or product ID: %s, %s' % (image_url, product_id), level=INFO)
            # print('\n Invalid image URL or product ID:', image_url, product_id)
            return []

        yield scrapy.Request(
            image_url,
            headers={"Referer": item.get("item_url") or "https://www.ebay.com/"},
            meta={"product_id": product_id},
        )

    def file_path(self, request, response=None, info=None, *, item=None):
        product_id = request.meta["product_id"]
        extension = self.extension_from_url(request.url)
        return f"{product_id}{extension}"

    @staticmethod
    def extension_from_url(url):
        suffix = Path(urlparse(url).path).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            return ".jpg"#suffix
        return ".jpg"
