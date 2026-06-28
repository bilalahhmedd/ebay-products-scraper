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
									"&_nkw=" + search_string.replace(' ','+').replace('_','+') + "&_ipg=60&_pgn="+str(x)+"&LH_ItemCondition=4", 
#									"&_nkw=" + search_string.replace(' ','+').replace('_','+') + "&_ipg=200&_pgn="+str(x), 
									callback=self.parse_link)

	def parse_search(self, response):

		self.logger.info("Search URL: %s", response.url)

		self.logger.info("Title: %s",
						response.css("title::text").get())

		products = response.css(".s-item")

		self.logger.info("Products: %d", len(products))

		with open("search.html", "wb") as f:
			f.write(response.body)

		for product in products:
			self.logger.info(product.css(".s-item__title::text").get())

			yield {
				"title": product.css(".s-item__title::text").get()
			}
	
	
	
	# Parse the search results
	def parse_link(self, response):
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
		
		
		# print("li.s-item:", len(response.css("li.s-item")))
		# print(".s-item:", len(response.css(".s-item")))
		# print("ul.srp-results:", len(response.css("ul.srp-results")))
		# print(".srp-results:", len(response.css(".srp-results")))
		# print(".srp-river-results", len(response.css(".srp-river-results")))

		# results = response.css("ul.srp-results").get()
		# print(results[:3000])

		# print("s-item" in response.text)
		# print(response.text.count("s-item"))

		# print("men shoes" in response.text)


		# product = response.css("li.s-item").get()
		# print(product[:1000])

		# product = response.css(".s-item").get()
		# print(product[:1000])

		# with open("search.html", "wb") as f:
		# 	f.write(response.body)

		# Extract the list of products
		# print('parsing page: ',response.url) 
		# results = response.xpath('//div/div/ul/li[contains(@class, "s-item" )]')
		# results = response.xpath('//li[contains(@class, "s-item" )]')
		# results = response.css(".s-item")
		# print('total products found: ',len(results))


		# Extract info for each product
		'''
		Will be writing prod_ids to universal list page by page
		'''
		
		prod_ids_page =[]
		product = results[9]

		# print("=" * 100)
		# print(product.get())
		# print("=" * 100)

		# product_url = product.css("a.s-card__link::attr(href)").get()
		# print("Product URL:", product_url)
		# product_id = match = re.search(r"/itm/(\d+)", product_url)
		# print("Product ID:", product_id.group(1) if product_id else None)
		# title = product.css(".s-card__title > span:first-child::text").get()
		# print("Product Name:", title)
		# status = product.css(
		# 				".s-card__subtitle span:first-child::text"
		# 			).get()
		# print("Product Status:", status)
		# price = product.css(".s-card__price::text").get()
		# print("Product Price:", price)
		# shipping = product.css(
		# 				".s-card__attribute-row:nth-child(3) span::text"
		# 			).get()
		# print("Product Shipping:", shipping)
		# location = product.css(
		# 				".s-card__attribute-row:last-child span::text"
		# 			).get()
		# print("Product Location:", location)
		# image_url = product.css(
		# 				"img.s-card__image::attr(src)"
		# 			).get()
		# image_url = image_url.replace(
		# 				"s-l140.webp",
		# 				"s-l500.jpg"
		# 			)
		# print("Product Image URL:", image_url)

		for product in results:
			product_url = product.css("a.s-card__link::attr(href)").get()
			print("Product URL:", product_url)
			product_id = match = re.search(r"/itm/(\d+)", product_url)
			print("Product ID:", product_id.group(1) if product_id else None)
			title = product.css(".s-card__title > span:first-child::text").get()
			print("Product Name:", title)
			status = product.css(
							".s-card__subtitle span:first-child::text"
						).get()
			print("Product Status:", status)
			price = product.css(".s-card__price::text").get()
			print("Product Price:", price)
			shipping = product.css(
							".s-card__attribute-row:nth-child(3) span::text"
						).get()
			print("Product Shipping:", shipping)
			location = product.css(
							".s-card__attribute-row:last-child span::text"
						).get()
			print("Product Location:", location)
			image_url = product.css(
							"img.s-card__image::attr(src)"
						).get()
			image_url = image_url.replace(
							"s-l140.webp",
							"s-l500.jpg"
						)
			print("Product Image URL:", image_url)

			summary_data = {
							"Title":title,
							"Status":status,
							"Location":location,
							"Price":price,
							"Shipping":shipping,
							"URL": product_url,
							"Image_URL": image_url
								}
			

		# for product in results:		
		# 	'''
		# 	First check if product url is not allready scrapped
		# 	'''
		# 	# product_url = product.xpath('.//a[@class="s-item__link"]/@href').extract_first()
		# 	# prod_id=product_url.split('itm/')[1].lstrip().split('?')[0]
		# 	product_url = product.css("a.s-card__link::attr(href)").get()

		# 	if not product_url:
		# 		continue

		# 	match = re.search(r"/itm/(\d+)", product_url)
		# 	if not match:
		# 		self.logger.warning("Could not extract product ID from URL: %s", product_url)
		# 		continue

		# 	prod_id = match.group(1)

		# 	#prod_id = prod_id.replace(' ','')
		# 	if int(prod_id) not in self.prod_urls_tracker:
		# 		# append prod_id to prod_urls_trakcer for local session
		# 		self.prod_urls_tracker.append(prod_id)
		# 		prod_ids_page.append(prod_id)
		# 		name = product.xpath('.//*[@class="s-item__title"]//text()').extract_first()
		# 		# Sponsored or New Listing links have a different class
		# 		if name == None:
		# 			name = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]/text()').extract_first()			
		# 			if name == None:
		# 				name = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]//text()').extract_first()			
		# 		if name == 'New Listing':
		# 			name = product.xpath('.//*[@class="s-item__title"]//text()').extract()[1]

		# 		# If this get a None result
		# 		if name == None:
		# 			name = "ERROR"

		# 		price = product.xpath('.//*[@class="s-item__price"]/text()').extract_first()
		# 		status = product.xpath('.//*[@class="SECONDARY_INFO"]/text()').extract_first()
		# 		seller_level = product.xpath('.//*[@class="s-item__etrs-text"]/text()').extract_first()
		# 		location = product.xpath('.//*[@class="s-item__location s-item__itemLocation"]/text()').extract_first()
				

		# 		# Set default values
		# 		stars = 0
		# 		ratings = 0

		# 		stars_text = product.xpath('.//*[@class="clipped"]/text()').extract_first()
		# 		if stars_text: stars = stars_text[:3]
		# 		ratings_text = product.xpath('.//*[@aria-hidden="true"]/text()').extract_first()
		# 		if ratings_text: ratings = ratings_text.split(' ')[0]

		# 		summary_data = {
		# 						"Name":name,
		# 						"Status":status,
		# 						"Seller_Level":seller_level,
		# 						"Location":location,
		# 						"Price":price,
		# 						"Stars":stars,
		# 						"Ratings":ratings,
		# 						"URL": product_url
		# 						}

		# 		# Go to the product details page
		# 		data = {'summary_data': summary_data}
		# 		yield scrapy.Request(product_url, meta=data, callback=self.parse_product_details_v1)
				
		# 	else:
		# 		print('skipping: ',prod_id)
		# 		continue 
		# # now append prod_ids of this page to universal list
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





		# spects
		spects={}
		spectdiv=response.xpath('//div[@class="ux-layout-section-module"]')[0] 
		allrows=spectdiv.xpath(".//div[@class='ux-layout-section__row']")
		for row in allrows: 
			labels=row.xpath(".//div[@class='ux-labels-values__labels']") 
			values=row.xpath(".//div[@class='ux-labels-values__values']") 
			if (len(labels)==len(values)): 
				for i in range(0,len(labels)): 
					name=(labels[i].xpath('.//*/text()').extract_first()) 
					val=(values[i].xpath('.//*/text()').extract_first())

		# try:
		# 	spects["EbayItemNumber"] = response.xpath("//div[@id='descItemNumber']/text()").extract_first()
		# except:
		# 	pass

		# spectdiv=response.xpath('//div[@class="vim x-about-this-item"]')[0]
		# allrows=spectdiv.xpath(".//div[@class='ux-layout-section__row']") 
		# for row in allrows:
		# 	labels=row.xpath(".//div[@class='ux-labels-values__labels']")  
		# 	values=row.xpath(".//div[@class='ux-labels-values__values']")  
		# 	if (len(labels)==len(values)):
		# 		for i in range(0,len(labels)):  
		# 			name=(labels[i].xpath('.//*/text()').extract_first()) 
		# 			val=(values[i].xpath('.//*/text()').extract_first()) 					
		# 			spects[name]=val
		# 			# data[name]=val
		
		



		# append dir_id and images_url to data table		
		url = data['URL']
		DirId = url.split('itm/')[1].lstrip().split('?')[0]
		
		# json.dump(spects, open("local/jsonspects/"+DirId+".json", 'wb'))
		with open("local/item-specs-jsons/"+DirId+".json", 'w') as fp:
			json.dump(spects, fp)
		data['prod_id']=DirId
		data['images_url']=linklist
		yield data









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
		



