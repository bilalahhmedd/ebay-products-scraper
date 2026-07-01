A production grade data scraper developed to acquire listing data (product details, images and item-specifications) from ebay.com

# Overview
E-commerce listing data acquistion demands end to end solution to scrape, validate and store data. This project is an implementation to acquire data from ebay using scrapy framework.
This project consists of two saparate scrapy bots.
##### scraping-ebay-1.0.3
##### scraping-ebay-2.0.0 [latest]
scraping-ebay-2.0.0 is stable, modernized and fully functional version at moment.

# Dependencies
* Python >= 3.8
* scrapy >= 2.16
* pandas
* pydantic

# Installation
* clone repo
* cd to scraping-ebay-2.0.0
* install dependencies (run pip install -r requirements.txt)

# How to run

* cd into scrapy-ebay-2.0.0 folder
* run command: ```scrapy crawl ebay -o output.csv -a search_query='ebay product name' -a pages=1```

# Output 
* local folder and output.csv file will be created
* local folder contains images sub-folder and item-specs-jsons subfolder containing json file per product id.
* Image folder contains multiple child folders named after product post ids.

# To increase number of scraped results

To increase number of scraped results, we need to increase number of pages to be scraped.
Each page contains 200 products posts.

``` scrapy crawl ebay -o output.csv -a search='your search query' -a pages='number of pages' ```

note: number of allowed pages to scrape per request may have limit set by ebay

# System Components

scraping-ebay-2.0.0 comprises following components

* spiders
    * ebay
* models
    * product
    * summary_product
    * image
* extractors
    * search_page_extractor
    * product_page_extractor
* pipelines
    * customImagePipeline
* utils
    * image_utils
    * selectors
    * url_utils

# Architecture
<Pre>
Spider
    │
    ├── Scheduling Requests
    ├── Pagination
    └── Passing Models

Extractors
    │
    ├── Parse HTML
    ├── Extract Data
    └── Build Domain Models

Models
    │
    └── Represent Business Objects

Pipelines
    │
    ├── Download Images
    ├── Export CSV
    └── (Soon) Save Item Specifics JSON
</pre>