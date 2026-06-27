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


# class customImagePipeline(ImagesPipeline):  
#     prod_ids = []

#     def get_media_requests(self, item, info):
#         data = item #item.get('data')
        
#         urls = item['images_url']

#         dir_id = data['prod_id']
#         for File_number, url in enumerate(urls):
#             yield Request(
#                 url=url,
#                 # data=item["data"],
#                 meta={'File_number': File_number,
#                         'dir': str(dir_id),
#                         # 'data': item.get('data'),
#                 }


#             # meta={'dir': item.get('Dir namenumber')}
            
#         )
        
    
#     def file_path(self, request, response=None, info=None):
#         file_name = request.meta.get('File_number')
#         dir_name = request.meta.get('dir')
        
#         return f"Images/{dir_name}/{file_name}.jpg"

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
