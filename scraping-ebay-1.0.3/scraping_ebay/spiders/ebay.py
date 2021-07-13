# -*- coding: utf-8 -*-
from typing import Sized
import scrapy


class EbaySpider(scrapy.Spider):
	
	name = "ebay"
	allowed_domains = ["ebay.com"]
	start_urls = ["https://www.ebay.com"]
	
	# Allow a custom parameter (-a flag in the scrapy command)
	def __init__(self, search="Tshirt,laced",pages=4,size='s'):
		# so first of all split serch based on comma
		self.search_list = search.split(',')
		self.pages=int(pages)
		self.size=size
		self.prod_urls_tracker = []
	def parse(self, response):
		# Extrach the trksid to build a search request	
		trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").extract()[0]       
		pages=self.pages+1
		# Build the url and start the requests
		for search_string in self.search_list:
			print('processing string: ',search_string)
			for x in range(1,self.pages+1):
				yield scrapy.Request("http://www.ebay.com/sch/i.html?_from=R40&_trksid=" + trksid +
									"&_nkw=" + search_string.replace(' ','+') + "&_ipg=200&_pgn="+str(x), 
									callback=self.parse_link)

	# Parse the search results
	def parse_link(self, response):
		# Extract the list of products 
		results = response.xpath('//div/div/ul/li[contains(@class, "s-item" )]')

		# Extract info for each product
		for product in results:		
			'''
			First check if product url is not allready scrapped
			'''
			product_url = product.xpath('.//a[@class="s-item__link"]/@href').extract_first()
			prod_id=product_url.split('itm/')[1].lstrip().split('?')[0]
			if prod_id not in self.prod_urls_tracker:
				self.prod_urls_tracker.append(prod_id)
				name = product.xpath('.//*[@class="s-item__title"]//text()').extract_first()
				# Sponsored or New Listing links have a different class
				if name == None:
					name = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]/text()').extract_first()			
					if name == None:
						name = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]//text()').extract_first()			
				if name == 'New Listing':
					name = product.xpath('.//*[@class="s-item__title"]//text()').extract()[1]

				# If this get a None result
				if name == None:
					name = "ERROR"

				price = product.xpath('.//*[@class="s-item__price"]/text()').extract_first()
				status = product.xpath('.//*[@class="SECONDARY_INFO"]/text()').extract_first()
				seller_level = product.xpath('.//*[@class="s-item__etrs-text"]/text()').extract_first()
				location = product.xpath('.//*[@class="s-item__location s-item__itemLocation"]/text()').extract_first()
				

				# Set default values
				stars = 0
				ratings = 0

				stars_text = product.xpath('.//*[@class="clipped"]/text()').extract_first()
				if stars_text: stars = stars_text[:3]
				ratings_text = product.xpath('.//*[@aria-hidden="true"]/text()').extract_first()
				if ratings_text: ratings = ratings_text.split(' ')[0]

				summary_data = {
								"Name":name,
								"Status":status,
								"Seller_Level":seller_level,
								"Location":location,
								"Price":price,
								"Stars":stars,
								"Ratings":ratings,
								"URL": product_url
								}

				# Go to the product details page
				data = {'summary_data': summary_data}
				yield scrapy.Request(product_url, meta=data, callback=self.parse_product_details)
				
			else:
				return 





			

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
							pass 
		

		# append dir_id and images_url to data table		
		url = data['URL']
		DirId = url.split('itm/')[1].lstrip().split('?')[0]
		data['prod_id']=DirId
		data['images_url']=linklist
		yield data
		
		
		
		




