A production grade data scraper developed to acquire listing data (product details, images and item-specifications) from ebay.com

# Overview
E-commerce listing data acquistion demands end to end solution to scrape, validate and store data. This project is an implementation to acquire data from ebay using scrapy framework.
This project consists of two saparate scrapy bots.
##### scraping-ebay-1.0.3
##### scraping-ebay-2.0.0 [latest]
scraping-ebay-2.0.0 is stable, modernized and fully functional version at moment.

# Quick Start
* git clone https://github.com/bilalahhmedd/ebay-products-scraper
* pip install -r requirements.txt
* cd scraping-ebay-2.0.0
* run command: ```scrapy crawl ebay -o products.csv -a search='ebay product name' -a pages=1```

### Command Arguments

| Argument | Type | Required | Default | Example | Description |
|----------|------|:--------:|---------|---------|-------------|
| `search` | String | ✅ | — | `"men shoes"` | Search keyword(s) to crawl. |
| `pages` | Integer | ❌ | `1` | `4` | Number of search result pages to scrape. |
| `output` | String | ✅ | — | `products.csv` | Output CSV file name. |

## Dependencies
* Python >= 3.8
* scrapy >= 2.16
* pandas
* pydantic

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

# License

MIT License

---

# Author

Bilal Ahmed

Data Engineer | Web Scraping | Machine Learning Data Pipelines