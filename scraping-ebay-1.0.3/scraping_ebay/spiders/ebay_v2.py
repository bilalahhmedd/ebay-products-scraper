# -*- coding: utf-8 -*-
from typing import Sized
from urllib import response
import scrapy
import pandas as pd
import os
import json

import re
#from local_utils import get_universal_ids
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
	allowed_domains = ["ebay.com","ebayimg.com"] # "ebay.co.uk"
	start_urls = ["https://www.ebay.com","https://www.ebay.co.uk"]

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
			# dont_filter=True,
		)

	def parse(self, response):
		# Extrach the trksid to build a search request	
		# trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").extract()[0]
		trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").extract()
		self.logger.info("Response URL: %s", response.url)
		self.logger.info("Page title: %s", response.css("title::text").extract_first())

		print('trksid: ',trksid)       
		pages=self.pages+1
		print('total pages to scrap: ',pages)
		# Build the url and start the requests
		for search_string in self.search_list:
			print('processing string: ',search_string)
			for x in range(1,self.pages+1):
# 				yield scrapy.Request("http://www.ebay.com/sch/i.html?_from=R40&_trksid=" + trksid +
# 									"&_nkw=" + search_string.replace(' ','+').replace('_','+') + "&_ipg=240&_pgn="+str(x)+"&LH_ItemCondition=4", 
# #									"&_nkw=" + search_string.replace(' ','+').replace('_','+') + "&_ipg=200&_pgn="+str(x), 
# 									callback=self.parse_link)
				yield scrapy.Request("http://www.ebay.com/sch/i.html?_from=R40" +
									"&_nkw=" + search_string.replace(' ','+').replace('_','+') + "&_ipg=10&_pgn="+str(x)+"&LH_ItemCondition=4", 
#									"&_nkw=" + search_string.replace(' ','+').replace('_','+') + "&_ipg=200&_pgn="+str(x), 
									callback=self.parse_search_page)


	# Parse the search results
	def parse_search_page(self, response):
		"""_summary_

		Args:
			response (_text_): html data coming from webpage

		Yields:
			_type_: list of product links, meta data of each product, 
		"""
		self.logger.info("URL: %s", response.url)
		self.logger.info("Title: %s", response.css("title::text").get())

		results = response.css("li.s-card")
		print('total products found: ',len(results))
		
		# Will be writing prod_ids to universal list page by page
		prod_ids_page =[]

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
			
			print("Product URL:", product_url)


			product_id = re.search(r"/itm/(\d+)", product_url)
			product_id = product_id.group(1) if product_id else None
			if int(product_id) not in self.prod_urls_tracker:
				
				# print("Product ID:", product_id)
				
				title = self.css_text(
							product,
							".s-card__title > span:first-child::text"
						)
				if not title:
					continue

				# print("Product Title:", title)
				
				status = self.css_text(
								product,
								".s-card__subtitle span:first-child::text"
							)

				if status:
					status = status.replace("·", "").strip()
				# print("Product Status:", status)
				price = self.css_text(
								product,
								".s-card__price::text"
							)
				# print("Product Price:", price)
				
				shipping = None

				for row in product.css(".s-card__attribute-row"):
					text = " ".join(row.css("span::text").getall()).strip()

					if "delivery" in text.lower():
						shipping = text
						break
				
				# print("Product Shipping:", shipping)
				
				location = None

				for row in product.css(".s-card__attribute-row"):
					text = " ".join(row.css("span::text").getall()).strip()

					if text.startswith("Located"):
						location = text.replace("Located in", "").strip()
						break
				
				# print("Product Location:", location)
				
				image_url = self.css_attr(
								product,
								"img.s-card__image::attr(src)"
							)
				# image_url = image_url.replace(
				# 				"s-l140.webp",
				# 				"s-l500.jpg"
				# 			)
				# print("Product Image URL:", image_url)

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
				yield scrapy.Request(product_url, meta=data, callback=self.parse_product_details_v1)
			else:
				print('skipping: ',product_id)
				continue	
		
		#pd.DataFrame({'prod-id':prod_ids_page}).to_csv('universal-prod-ids.csv',mode='a',header=False)


	# Parse details page for each product
	def parse_product_details(self, response):

		# Get the summary data
		data = response.meta['summary_data']

		# Add more data from details page
		data['UPC'] = response.xpath('//h2[@itemprop="gtin13"]/text()').extract_first()
		links=response.xpath("//img/@src")
		html=""
		linklist=[]
		#set size of images
		img_size='s-l500'
		if self.size =='m':
			img_size='s-l1000'
		elif self.size=='l':
			img_size='s-l2000'


		for link in links:
			url=link.get()
			if any(extension in url for extension in [".jpg"]):
				if "s-l64" in url:
					url=url.replace("s-l64",img_size)
					if url not in linklist:
						linklist.append(url)





		# spects
		allspect=response.xpath('//div[@class="itemAttr"]/div/table/tr')
		for spect in allspect:
			row=spect.xpath('.//td') 
			if(len(row)==4 ):

				try:
					
					name=spect.xpath('.//td/text()')[0].extract() 
					name=name.strip()             
					value=spect.xpath('.//td/span/text()')[0].extract() 
					val = value.split() 
					name1=spect.xpath('.//td/text()')[2].extract() 
					name1=name1.strip() 
					value1=spect.xpath('.//td/span/text()')[1].extract() 
					val1 = value1.split()
					data[name]=" ".join(val)
					data[name1]=" ".join(val1)
					# print(name) 
					# print(val) 
					# print(name1) 
					# print(val1) 
				except:

					try:
						name=spect.xpath('.//td/text()')[0].extract() 
						name=name.strip()             
						value=spect.xpath('.//td/div/span/text()')[0].extract() 
						val = value.split() 
						value1=spect.xpath('.//td/span/text()')[0].extract() 
						val1 = value1.split() 


						nn=spect.xpath('//td[@class="attrLabels"]/text()').extract()  

						name1=nn[1] 
						name1=name1.strip() 
						
						data[name]=" ".join(val)
						data[name1]=" ".join(val1)
					except:
						try:
							name=spect.xpath('.//td/text()')[0].extract() 
							name=name.strip()             
								
							name1=spect.xpath('.//td/text()')[2].extract() 
							name1=name1.strip() 
							value1=spect.xpath('.//td/span/text()')[0].extract() 
							val1 = value1.split() 
							vl=spect.xpath('.//td')[1] 
							val=vl.xpath('.//span/span/text()')[0].extract() 
							val=val.split()
							data[name]=" ".join(val)
							data[name1]=" ".join(val1)
							# print(name) 
							# print(val) 
							# print(name1) 
							# print(val1) 
						except:
							try: 
								name=spect.xpath('.//td/text()')[0].extract() 
								name=name.strip()             
								name1=spect.xpath('.//td/text()')[2].extract() 
								name1=name1.strip() 
								value=spect.xpath('.//td/span/text()')[0].extract() 
								val = value.split() 
								vl=spect.xpath('.//td')[3] 
								val1=vl.xpath('.//span/span/text()')[0].extract() 
								val1=val1.split() 
								data[name]=" ".join(val)
								data[name1]=" ".join(val1)
								# print(name) 
								# print(val) 
								# print(name1) 
								# print(val1) 
							except: 
								pass 

		# append dir_id and images_url to data table		
		url = data['URL']
		DirId = url.split('itm/')[1].lstrip().split('?')[0]
		data['prod_id']=DirId
		data['images_url']=linklist
		yield data





	def parse_product_details_v1(self, response):
		"""_summary_ parses attributes data of each product 

		Args:
			response (_text_): product url

		Yields:
			_dict_: product attributes and metadata
		"""

		self.logger.info("=" * 80)
		self.logger.info("Parsing product")
		self.logger.info(response.url)
		self.logger.info(response.css("title::text").get())

		if not os.path.exists('local/item-specs-jsons'):
			os.makedirs('local/item-specs-jsons')


		# Get the summary data
		data = response.meta['summary_data']

		# Add more data from details page
		data['UPC'] = response.xpath('//h2[@itemprop="gtin13"]/text()').extract_first()
		links=response.xpath("//img/@src")
		html=""
		linklist=[]
		#set size of images
		img_size='s-l500'
		if self.size =='m':
			img_size='s-l1000'
		elif self.size=='l':
			img_size='s-l2000'


		for link in links:
			url=link.get()
			if any(extension in url for extension in [".jpg"]):
				if "s-l64" in url:
					url=url.replace("s-l64",img_size)
					if url not in linklist:
						linklist.append(url)

		# Extract Item Specifics
		section = response.css("div[data-testid='x-about-this-item']")

		specs = self.extract_specs(section)
		
		self.logger.info(specs)

		# append dir_id and images_url to data table		
		url = data['Product_URL']
		DirId = url.split('itm/')[1].lstrip().split('?')[0]
		
		# json.dump(spects, open("local/jsonspects/"+DirId+".json", 'wb'))
		# with open("local/item-specs-jsons/"+DirId+".json", 'w') as fp:
		# 	json.dump(spects, fp)
		# data['prod_id']=DirId
		# data['images_url']=linklist
		# yield data


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
		



