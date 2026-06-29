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

import logging

logger = logging.getLogger(__name__)


class customImagePipeline(ImagesPipeline):  
    prod_ids = []

    def get_media_requests(self, item, info):
        # data = item #item.get('data')
        
        # urls = item['images_url']
        image_urls = item.get("image_urls", [])
        dir_id = item['Product_ID']

        if not image_urls:
            logger.warning(
                "No images found for product %s",
                item.get("Product_ID", "unknown")
            )
            return
        logger.info(
            "Downloading %d images for %s",
            len(image_urls),
            item["Product_ID"]
        )

        for index, url in enumerate(image_urls, start=1):

            yield Request(
                url=url,
                meta={
                    "image_number": index,
                    "product_id": item["Product_ID"],
                },
            )

        # for File_number, url in enumerate(urls):
        #     yield Request(
        #         url=url,
        #         # data=item["data"],
        #         meta={'File_number': File_number,
        #                 'dir': str(dir_id),
        #                 # 'data': item.get('data'),
        #         }
        # )
        
    
    def file_path(self, request, response=None, info=None,*, item=None):
            image_number = request.meta["image_number"]
            product_id = request.meta["product_id"]

            return (
                f"images/{product_id}/"
                f"{image_number:02d}.jpg"
                )
        
        # file_name = request.meta.get('File_number')
        # dir_name = request.meta.get('dir')
        
        # return f"Images/{dir_name}/{file_name}.jpg"

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

# class EbayProductImagePipeline(FilesPipeline):
#     def get_media_requests(self, item, info):
#         image_url = item.get("image_url")
#         product_id = item.get("product_id")

#         if not image_url or not product_id:
#             print('\n Invalid image URL or product ID:', image_url, product_id)
#             return []

#         yield scrapy.Request(
#             image_url,
#             headers={"Referer": item.get("item_url") or "https://www.ebay.com/"},
#             meta={"product_id": product_id},
#         )

#     def file_path(self, request, response=None, info=None, *, item=None):
#         product_id = request.meta["product_id"]
#         extension = self.extension_from_url(request.url)
#         return f"{product_id}{extension}"

#     @staticmethod
#     def extension_from_url(url):
#         suffix = Path(urlparse(url).path).suffix.lower()
#         if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
#             return ".jpg"#suffix
#         return ".jpg"
