# ebay-products-scraper
An ebay-scraper project developed using scrapy framework. It scraps product details and images from ebay.com.

# Dependencies
* scrapy
* pandas
* json

check requirements.txt 
# Installation
* clone repo
* cd to scraping-ebay-1.0.3
* install dependencies (run pip install -r requirements.txt)

# Running Scraper

* cd scrapy-ebay-1.0.3 folder via terminal
* run command 
    * to generate data: ```scrapy crawl ebay_spider_01 -o output.csv -a search_query='ebay product name' ```
    * to count number of products available to scrap on ebay: ```scrapy crawl ebay_result_count -o output.csv -a search_query='ebay product name' ```

# Output 
* local folder and output.csv file will be created
* local folder contains images sub-folder and item-specs-jsons subfolder containing json file per product id.
* Image folder contains multiple child folders named after product post ids.

# To increase number of scraped results

To increase number of scraped results, we need to increase number of pages to be scraped.
Each page contains 200 products posts.

``` scrapy crawl ebay -o output.csv -a search='your search query' -a pages='number of pages' ```

note: number of allowed pages can have limit set by ebay