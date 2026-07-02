# -*- coding: utf-8 -*-
import scrapy
import json
from pathlib import Path

# local imports
from scraping_ebay.extractors.search_page_extractor import SearchPageExtractor
from scraping_ebay.extractors.product_page_extractor import ProductPageExtractor

class EbaySpider(scrapy.Spider):
	"""_summary_ <-- this spider scrapes products listing data (csv,images folder). based on search query and number of pages, it scrapes web pages of allowed domain (ebay.com, ebay.uk)
					it also avoids duplication by maintaining history of product ids.

	Args:
		scrapy (_Spider_): _Spider class_
		name	(text): name of spider
		allowed_domains (list): only scrap mentioned domains
		start_urls (list): set of urls to initial request

	Yields:
		folder of csv: files containing product details, attributes data of corresponding products ids
		folder of images: folders containing images of corresponding products ids
		folder of json: files containing item specifics of corresponding products ids 
	"""
	name = "ebay"
	allowed_domains = ["ebay.com","ebayimg.com"]
	start_urls = ["https://www.ebay.com"]

	def __init__(self, search="Tshirt,laced",pages=4,size='s'):
		"""_summary_

		Args:
			search (str, optional): set of product names to be scraped "Tshirt,laced".
			pages (int, optional): number of pages for each product to be scraped
			size (str, optional): size (s,m,l) of images for each product to be scraped
		"""
		# so first of all split serch based on comma
		self.search_list = search.split(',')
		self.pages=max(1,int(pages))
		self.size=size

	
	async def start(self):
		yield self.homepage_request()
	
	def homepage_request(self):
		return scrapy.Request(
			"https://www.ebay.com/",
			callback=self.parse
		)
	
	def parse(self, response):
			"""Spider entry point."""
			yield from self.schedule_search_requests()

	def schedule_search_requests(self):
		# Build the url and start the requests
		for search_string in self.search_list:
			print('processing string: ',search_string)
			for page in range(1,self.pages+1):
				yield scrapy.Request(
									"http://www.ebay.com/sch/i.html"
						 			f"?_from=R40"
									f"&_nkw={search_string.replace(' ','+').replace('_','+')}"
									f"&_ipg=60"
									f"&_pgn={page}"
									f"&LH_ItemCondition=4",

									callback=self.parse_search_page)


	# Parse the search results
	def parse_search_page(self, response):
		"""_summary_

		Args:
			response (_text_): html data coming from webpage

		Yields:
			_type_: list of product links, meta data of each product, 
		"""
		results = response.css("li.s-card")
		print('total products found: ',len(results))

		for product in results:
			summary = SearchPageExtractor(product_node=product).extract()
			# print(f'summary: {summary}')
			data = {'summary': summary}
			yield scrapy.Request(summary.product_url, meta=data, callback=self.parse_product_details)
				

	def parse_product_details(self, response):
		"""_summary_ parses attributes data of each product 

		Args:
			response (_text_): product url

		Yields:
			_dict_: product attributes and metadata
		"""

		summary = response.meta['summary']
		product = ProductPageExtractor(response=response, summary=summary).extract()
		
		# --------------------------------------------------
		# Temporary: Save Item Specifics JSON
		# --------------------------------------------------

		output_dir = Path("local/item-specs-jsons")
		output_dir.mkdir(parents=True, exist_ok=True)

		json_path = output_dir / f"{product.product_id}.json"

		with open(json_path, "w", encoding="utf-8") as fp:
			json.dump(
				product.item_specifics,
				fp,
				indent=4,
				ensure_ascii=False,
			)
		
		yield product