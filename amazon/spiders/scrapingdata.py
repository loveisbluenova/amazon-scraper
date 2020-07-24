from scrapy import Request
import scrapy
from scrapy.item import Item, Field
from lxml.html import fromstring
import requests
import json


class SiteProductItem(Item):
    asin = Field()
    product_name = Field()
    sales_status = Field()
    seller = Field()
    price = Field()
    review_stars = Field()
    customer_review_text = Field()


class AmazonScraper (scrapy.Spider):
    name = "scrapingdata"
    allowed_domains = ['www.amazon.com']
    DOMAIN_URL = 'https://amazon.com.au'
    START_URL = 'https://www.amazon.com.au/dp/'

    def __init__(self, **kwargs):
        self.asin = kwargs['asin']
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/57.0.2987.133 Safari/537.36"}

    def start_requests(self):
        yield Request(url=self.START_URL + self.asin,
                      callback=self.parse_page,
                      headers=self.headers,
                      dont_filter=True
                      )

    def parse_page(self, response):

        product_name = response.xpath('//span[@id="productTitle"]/text()')[0].extract().strip()

        review_stars = ''
        pre_review_stars = response.xpath(
            '//div[@id="averageCustomerReviews_feature_div"]/div[@id="averageCustomerReviews"]'
            '//span[@id="acrPopover"]//span[@class="a-icon-alt"]/text()').extract()
        if pre_review_stars:
            review_stars = pre_review_stars[0]

        customer_review_text = ''
        pre_customer_review_text = response.xpath('//span[@id="acrCustomerReviewText"]/text()').extract()
        if pre_customer_review_text:
            customer_review_text = pre_customer_review_text[0]

        sales_status = 'Inactive'
        price = ''
        seller = ''
        available_info = response.xpath(
            '//div[@id="availability_feature_div"]/div[@id="availability"]'
            '//span[@class="a-declarative"]//a/@href').extract()
        if available_info:
            sales_status = "active"
            available_info_url = self.DOMAIN_URL + available_info[0]

            response_avail = requests.get(available_info_url, headers=self.headers)

            price_info_list = fromstring(response_avail.text).xpath(
                '//div[@id="olpOfferListColumn"]//div[@class="a-column a-span2 olpPriceColumn"]'
                '/span[@class="a-size-large a-color-price olpOfferPrice a-text-bold"]//text()')
            if price_info_list:
                price = price_info_list[0].strip()

            seller_info_list = fromstring(response_avail.text).xpath('//h3/img/@alt')
            if seller_info_list:
                seller = seller_info_list[0]

        product = SiteProductItem()
        product['asin'] = self.asin
        product['product_name'] = product_name
        product['review_stars'] = review_stars
        product['customer_review_text'] = customer_review_text
        product['sales_status'] = sales_status
        product['price'] = price
        product['seller'] = seller

        yield product

