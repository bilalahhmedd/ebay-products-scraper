# -*- coding: utf-8 -*-
# from urllib import response
import scrapy
# from typing import Sized


class EbayResultCountSpider(scrapy.Spider):
    name = 'ebay_result_count'
    allowed_domains = ['ebay.com']
    start_urls = ['http://ebay.com/']

    def __init__(self, search="Tshirt,laced"):
        # so first of all split serch based on comma
        self.search_list = search.split(',')

    def parse(self, response):
		# Extrach the trksid to build a search request	
        trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").extract()[0]       
		
		# Build the url and start the requests
        for search_string in self.search_list:
            print('processing string: ',search_string)
            
            yield scrapy.Request("http://www.ebay.com/sch/i.html?_from=R40&_trksid=" + trksid +
                                    "&_nkw=" + search_string.replace(' ','+').replace('_','+') + "&_ipg=200", 
                                    callback=self.parse_link)

	# Parse the search results
    def parse_link(self, response):
        ItemCount=response.xpath('//h1[@class="srp-controls__count-heading"]/span/text()')[0].extract() 
        keyWord=t=response.xpath('//h1[@class="srp-controls__count-heading"]/span/text()')[1].extract()
        yield{
            "KeyWord":keyWord,
            "ResultCount":ItemCount
        }