# -*- coding: utf-8 -*-
from typing import Sized
from urllib import response
import scrapy
import pandas as pd
import os
import json
from pathlib import Path
import re

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
	"""
	name = "ebay_spider_02"
	allowed_domains = ["ebay.com","ebayimg.com"]
	start_urls = ["https://www.ebay.com"]

	def __init__(self, search_query="Tshirt,laced",pages=4,size='s'):
		"""_summary_

		Args:
			search_query (str, optional): set of product names to be scraped "Tshirt,laced".
			pages (int, optional): number of pages for each product to be scraped
			size (str, optional): size (s,m,l) of images for each product to be scraped
		"""
		# so first of all split serch based on comma
		self.search_list = search_query.split(',')
		self.pages=max(1,int(pages))
		self.size=size
		# read universal prod_ids and pass to tracker
		self.prod_urls_tracker = self.get_universal_ids()#self.read_univeral_prod_ids()
		print('total universal ids: ',len(self.prod_urls_tracker))
	
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
			# get product url and skip sponsored listing links
			product_url = self.css_attr(
							product,
							"a.s-card__link::attr(href)"
						)
			if not product_url:
				continue

			if "/itm/" not in product_url:
				continue

			product_id = re.search(r"/itm/(\d+)", product_url)
			product_id = product_id.group(1) if product_id else None
			if int(product_id) not in self.prod_urls_tracker:
				
				title = self.css_text(
							product,
							".s-card__title > span:first-child::text"
						)
				if not title:
					continue

				status = self.css_text(
								product,
								".s-card__subtitle span:first-child::text"
							)

				if status:
					status = status.replace("·", "").strip()
				
				price = self.css_text(
								product,
								".s-card__price::text"
							)
				
				shipping = None

				for row in product.css(".s-card__attribute-row"):
					text = " ".join(row.css("span::text").getall()).strip()

					if "delivery" in text.lower():
						shipping = text
						break
				
				location = None
				for row in product.css(".s-card__attribute-row"):
					text = " ".join(row.css("span::text").getall()).strip()

					if text.startswith("Located"):
						location = text.replace("Located in", "").strip()
						break
				
				image_url = self.css_attr(
								product,
								"img.s-card__image::attr(src)"
							)

				summary_data = {
								"Product_ID":product_id,
								"Title":title,
								"Status":status,
								"Location":location,
								"Price":price,
								"Shipping":shipping,
								"Product_URL": product_url,
								"Image_URL": image_url
									
								}
				data = {'summary_data': summary_data}
				yield scrapy.Request(product_url, meta=data, callback=self.parse_product_details)
			else:
				print('skipping: ',product_id)
				continue	

	def parse_product_details(self, response):
		"""_summary_ parses attributes data of each product 

		Args:
			response (_text_): product url

		Yields:
			_dict_: product attributes and metadata
		"""

		self.logger.info("=" * 80)
		self.logger.info("Parsing product")
		self.logger.info(response.css("title::text").get())

		# implement gallery images extraction

		images = response.css("img")

		self.logger.info(f"Total images: {len(images)}")

		image_urls = []

		gallery = response.css("div.ux-image-carousel img")
		for img in gallery:

			url = (
				img.css("::attr(data-zoom-src)").get()
				or img.css("::attr(src)").get()
				or img.css("::attr(data-src)").get()
			)

			if not url:
				continue

			if "i.ebayimg.com" not in url:
				continue

			image_urls.append(url)

		image_urls = list(dict.fromkeys(image_urls))
		

		data = response.meta['summary_data']

		# Extract Item Specifics
		section = response.css("div[data-testid='x-about-this-item']")
		item_specifics = self.extract_specs(section)
		
		# Create directory if it doesn't exist
		output_dir = Path("local/item-specs-jsons")
		output_dir.mkdir(parents=True, exist_ok=True)
		DirId = data['Product_ID']
		json_path = output_dir / f"{DirId}.json"
		with open(json_path, "w", encoding="utf-8") as fp:
			json.dump(
				item_specifics,
				fp,
				indent=4,
				ensure_ascii=False
			)
		# populate data dictionary with item specifics
		data["Brand"] = item_specifics.get("Brand")
		data["Department"] = item_specifics.get("Department")
		data["Color"] = item_specifics.get("Color")
		data["Size"] = (
			item_specifics.get("US Shoe Size")
			or item_specifics.get("Size")
		)
		data["UPC"] = item_specifics.get("UPC")
		data["MPN"] = item_specifics.get("MPN")
		data["Model"] = item_specifics.get("Model")
		
		data['image_urls']=image_urls
		
		yield data


	def extract_specs(self, section):
		specs = {}

		for spec in section.css("dl[data-testid='ux-labels-values']"):
			key = " ".join(
				t.strip()
				for t in spec.css("dt ::text").getall()
				if t.strip()
			)

			value = " ".join(
				t.strip()
				for t in spec.css("dd ::text").getall()
				if t.strip()
			)
			value = self.clean_spec_value(value)
			if key:
				specs[key] = value

		return specs

	def clean_spec_value(self,value):
		remove = [
			"Read more about the condition",
			"See all condition definitions",
			"opens in a new window or tab",
		]

		for text in remove:
			value = value.replace(text, "")

		return " ".join(value.split())

	def css_text(self, node, selector, default=None):
		"""
		Return stripped text from a CSS selector.
		"""
		value = node.css(selector).get()
		if value:
			return value.strip()
		return default


	def css_attr(self, node, selector, default=None):
		"""
		Return stripped attribute value.
		"""
		value = node.css(selector).get()
		if value:
			return value.strip()
		return default




	def read_univeral_prod_ids(self):
		try:
			return list(pd.read_csv('universal-prod-ids.csv')['prod-id'])
		except FileNotFoundError:
			print('creating file universal-prod-ids.csv')
			# create new csv file
			pd.DataFrame(columns=['prod-id']).to_csv('universal-prod-ids.csv')
			return list(pd.read_csv('universal-prod-ids.csv')['prod-id'])
		
	def get_universal_ids(self):

		ids =[]
		all_csvs=[]
		# for root, directories, files in os.walk("../../", topdown=False):
		for root, directories, files in os.walk("./", topdown=False):
			for name in files:
				f=(os.path.join(root, name))
				if f.endswith((".csv")):
					all_csvs.append(f)
		# iterate thorugh each csv file and build list of universal keys out of it
		for csv_file in all_csvs:
			try:
				df=pd.read_csv(csv_file)
				for id in list(df['prod_id']):
						ids.append(int(id))
			except:
				print(csv_file,' is empty')
				pass
			# df=pd.read_csv(csv_file)
			# for id in list(df['prod_id']):
			# 		ids.append(int(id))


		return ids	
		



