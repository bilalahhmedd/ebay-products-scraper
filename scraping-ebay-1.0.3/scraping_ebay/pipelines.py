# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http.request import Request

class ScrapingEbayPipeline(object):
    def process_item(self, item, spider):
        yield item.get('data')
        images=item.get('images')
        urls = images[0]
        dir_id = images[1]

        for e,i in enumerate(urls):
            yield Request(url=i,meta={'File_number':e,'dir':dir_id})

    
    def file_path(self, request, response=None, info=None):
        file_name = request.meta.get('File_number')
        dir_name = request.meta.get('dir')
        
        return f"Images/{dir_name}/{file_name}.jpg" 


class myImagePipeline(ImagesPipeline):
    def process_item(self, item, spider):
        images=item.get('images')
        urls = images[0]
        dir_id = images[1]

        for e,i in enumerate(urls):
            yield Request(url=i,meta={'File_number':e,'dir':dir_id})

    
    def file_path(self, request, response=None, info=None):
        file_name = request.meta.get('File_number')
        dir_name = request.meta.get('dir')
        
        return f"Images/{dir_name}/{file_name}.jpg"    
    

# we are using this pipeline right now
class customImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        data = item.get('data')
        print('type of data: ',type(data))
        images = item.get('images')
        print('type of images', type(images))
        urls = images[0]
        dir_id = images[1]
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

