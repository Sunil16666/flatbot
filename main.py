import os

import requests
import scrapy
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from scrapy.crawler import CrawlerProcess
from dotenv import load_dotenv

# from availability_checker import AvailabilityChecker


class EstateItem(scrapy.Item):
    """
    Represents an item scraped from estate listings.
    """
    Title = scrapy.Field()
    Price = scrapy.Field()
    Area = scrapy.Field()
    Rooms = scrapy.Field()
    url = scrapy.Field()


PRICE_MIN = 300
PRICE_MAX = 800
SIZE_MIN = 20
ROOMS = 1


class SpiderIW(scrapy.Spider):
    """
    Spider for scraping estate listings from immowelt.de.
    """
    name = 'spider_iw'

    start_urls = [
        f'https://www.immowelt.de/liste/konstanz-koenigsbau/wohnungen/mieten?ami={SIZE_MIN}&d=true&lids=462735'
        f'&lids=462751&lids=462733&lids=462766&lids=462749&lids=462734&lids=462758&pma={PRICE_MAX}&pmi='
        f'{PRICE_MIN}&sd=DESC&sf=TIMESTAMP&sp=1',
    ]

    def parse(self, response, **kwargs):
        """
        Parse the HTML response and extract estate item details.
        """
        offer_elements = response.css('[class^="EstateItem-"]')

        for offer in offer_elements:
            title = offer.css('h2::text').get()
            price = offer.css('[data-test="price"]::text').get()
            area = offer.css('[data-test="area"]::text').get()
            rooms = offer.css('[data-test="rooms"]::text').get()
            offer_url = offer.css('a::attr(href)').get()

            item = EstateItem(
                Title=title,
                Price=price,
                Area=area,
                Rooms=rooms,
                url=offer_url,
            )
            yield item


class SpiderWGG(scrapy.Spider):
    """
    Spider for scraping estate listings from wg-gesucht.de.
    """
    name = 'spider_wgg'

    start_urls = [
            f'https://www.wg-gesucht.de/1-zimmer-wohnungen-und-wohnungen-in-Muenchen.90.1+2.1.0.html?offer_filter=1'
            f'&city_id=74&sort_order=0&noDeact=1&categories[]=1&categories[]=2&rent_types[]=0&sMin={SIZE_MIN}&rMax='
            f'{PRICE_MAX}&exc=2',
        ]

    def parse(self, response, **kwargs):
        """
        Parse the HTML response and extract estate item details.
        """
        offer_elements = response.css('div.wgg_card.offer_list_item')

        for offer in offer_elements:
            price = offer.css('div.row.noprint.middle div.col-xs-3 b::text').get()
            area = offer.css('div.row.noprint.middle div.col-xs-3.text-right b::text').get()
            rooms = offer.css('div.col-xs-11 span::text').re_first(r'(\d+-\w+-\w+)')
            offer_url = "https://www.wg-gesucht.de" + offer.css('a.detailansicht::attr(href)').get()

            item = EstateItem(
                Price=price,
                Area=area,
                Rooms=rooms,
                url=offer_url,
            )
            yield item


class SpiderKA(scrapy.Spider):
    """
    Spider for scraping estate listings from kleinanzeigen.de.
    """
    name = 'spider_ka'

    start_urls = [
            f'https://www.kleinanzeigen.de/s-wohnung-mieten/muenchen/anzeige:angebote/preis:{PRICE_MIN}:{PRICE_MAX}/'
            f'c203l9386+wohnung_mieten.qm_d:{SIZE_MIN}%2C+wohnung_mieten.zimmer_d:{ROOMS}%2C',
        ]

    def parse(self, response, **kwargs):
        """
        Parse the HTML response and extract estate item details.
        """
        offer_elements = response.css('[class="aditem"]')

        for offer in offer_elements:
            title = offer.css('.text-module-begin a::text').get()
            price = offer.css('.aditem-main--middle--price-shipping--price::text').get().strip()
            area = offer.css('.simpletag:nth-child(1)::text').get()
            rooms = offer.css('.simpletag:nth-child(2)::text').get()
            offer_url = 'https://www.kleinanzeigen.de' + offer.css('.aditem-main--middle a::attr(href)').get()

            item = EstateItem(
                Title=title,
                Price=price,
                Area=area,
                Rooms=rooms,
                url=offer_url,
            )
            yield item


class EstatePipeline:
    collection_name = 'listings'

    def __init__(self, mongo_uri, mongo_db, ntfy_topic):
        """
        Pipeline for storing items in MongoDB and sending notifications using ntfy.

        Args:
            mongo_uri (str): MongoDB connection URI.
            mongo_db (str): MongoDB database name.
            ntfy_topic (str): The topic to which notifications will be sent using ntfy.
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.ntfy_topic = ntfy_topic
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            ntfy_topic=crawler.settings.get('NTFY_TOPIC', 'default')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        """
        Process the scraped item.

        Args:
            item (scrapy.Item): The scraped item.
            spider (scrapy.Spider): The spider instance.

        Returns:
            scrapy.Item: The processed item.
        """
        url = item['url']
        existing_item = self.db[self.collection_name].find_one({'url': url})

        if existing_item:
            spider.logger.info(f"Item with URL '{url}' already exists. Skipping...")
        else:
            try:
                inserted_item = self.db[self.collection_name].insert_one(dict(item))
                spider.logger.info(f"Item with URL '{url}' inserted into the database.")

                # Format the notification message
                message = f"New offer: {item['Title']}\nPrice: {item['Price']}\nArea: {item['Area']}\nRooms: {item['Rooms']}"

                # Send the notification to the specific topic using an HTTP POST request
                ntfy_url = f"https://ntfy.sh/{self.ntfy_topic}"
                requests.post(
                    ntfy_url,
                    data=message.encode(encoding='utf-8'),
                    headers={'Actions': f'view, Open link, {url}'}
                )
            except DuplicateKeyError:
                spider.logger.warning(f"Duplicate key error for item with URL '{url}'. Skipping...")

        return item


if __name__ == "__main__":
    load_dotenv()
    # MongoDB's connection details
    mongo_uri = os.getenv('MONGO_URI')
    mongo_db = os.getenv('MONGO_DB')
    ntfy_topic = os.getenv('NTFY_TOPIC')

    # Start availability checker
    # availability_checker = AvailabilityChecker(mongo_uri, mongo_db)
    # availability_checker.start_checking_availability()

    # Configure and start the crawler process
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'LOG_LEVEL': 'INFO',
        'ITEM_PIPELINES': {
            '__main__.EstatePipeline': 300,
        },
        'MONGO_URI': mongo_uri,
        'MONGO_DATABASE': mongo_db,
        'NTFY_TOPIC': ntfy_topic,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 3,
    })

    # Add spiders to the process
    process.crawl(SpiderIW)
    process.crawl(SpiderWGG)
    process.crawl(SpiderKA)

    # Start the crawling process
    process.start()
