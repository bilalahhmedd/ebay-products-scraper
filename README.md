# ebay-products-scraper
An ebay-scraper project developed using scrapy framework. It will scrap product details and images from ebay.com.

# Dependencies
scrapy
pandas
json

check requirements.txt 

Simply run pip install -r requirements.txt to install dependencies.

# Installation
Just clone repo to your system and it is ready to run.
Cd to scraping-ebay-1.0.3 folder and install dependencies using following command

pip install -r requirements.txt

# Running Scraper

cd to scrapy=ebay-1.0.3 folder using shell and run following command

scrapy crawl ebay -o output.csv -a search='your search query'

It will generate local folder inside directory and also create output.csv file.
Local folder contains images folder and item-specs-jsons containing one json file per product id.
Image folder contains multiple folders named after product posts ids.

# To increase number of scraped results

To increase number of scraped results, we need to increased number of pages to be scraped.
Each page contains 200 products posts.

pass pages as argument to command as following

scrapy crawl ebay -o output.csv -a search='your search query' -a pages='number of pages'

Suppose you want to download 4000 images of Nike shoes from ebay.
So each page contain 200 posts and each post contain 10 images on average.
So we have 2000 images for one page.
So we set pages =2
It will scrap around 4000 images inside 400 folders (one folder for one product post)
