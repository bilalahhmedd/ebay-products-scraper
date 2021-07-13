# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http.request import Request


class customImagePipeline(ImagesPipeline):  
    prod_ids = []

    def get_media_requests(self, item, info):
        data = item #item.get('data')
        
        urls = item['images_url']

        dir_id = data['prod_id']
        for File_number, url in enumerate(urls):
            yield Request(
                url=url,
                # data=item["data"],
                meta={'File_number': File_number,
                        'dir': str(dir_id),
                        # 'data': item.get('data'),
                }


            # meta={'dir': item.get('Dir namenumber')}
            
        )
        
    
    def file_path(self, request, response=None, info=None):
        file_name = request.meta.get('File_number')
        dir_name = request.meta.get('dir')
        
        return f"Images/{dir_name}/{file_name}.jpg"







    # def get_media_requests(self, item, info):
    #     yield Request(
    #         url=item["Image Url"],
    #         # data=item["data"],
    #         meta={'File_number': item.get('File number'),
    #                 'dir': item.get('Dir name'),
    #                 # 'data': item.get('data'),
                    

    #         }


    #         # meta={'dir': item.get('Dir namenumber')}
            
    #     )
    
    # def file_path(self, request, response=None, info=None):
    #     file_name = request.meta.get('File_number')
    #     dir_name = request.meta.get('dir')
        
    #     return f"Images/{dir_name}/{file_name}.jpg"
