# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Stock(scrapy.Item):
    # define the fields for your item here like:
    ticker = scrapy.Field()
    name = scrapy.Field()
    intraday_price = scrapy.Field()
    price_change = scrapy.Field()
    percent_change = scrapy.Field()
    volume = scrapy.Field()
    avg_vol_3_month = scrapy.Field()
    market_cap = scrapy.Field()
    pe_ratio_ttm = scrapy.Field()
    sector = scrapy.Field()
