from __future__ import absolute_import
import scrapy
from src.items import Stock
from scrapy import Selector
import re
from scrapy.shell import inspect_response

class StocksSpider(scrapy.Spider):
  name = 'stocks'
  start_urls = [
    'https://finance.yahoo.com/screener/predefined/ms_basic_materials?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_communication_services?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_consumer_defensive?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_energy?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_financial_services?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_healthcare?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_industrials?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_real_estate?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_technology?offset=0&count=100',
    'https://finance.yahoo.com/screener/predefined/ms_utilities?offset=0&count=100',
  ]

  def parse(self, response):
    sector = re.search("ms_[^?]+", response.url).group()[3:]
    stocks = []
    amt = { 'k': 1000, 'M': 1000000, 'B': 1000000000, 'T': 1000000000000 }
    offset = int(re.search("offset=\d+", response.url).group()[7:])

    res_count = response.xpath('//div[@id="fin-scr-res-table"]/div[1]/div[1]/span[2]//text()').get()
    if res_count != None:
      minimum, maximum, total = int(res_count.split('-')[0]), int(res_count.split('-')[1].split(' ')[0]), int(res_count.split('-')[1].split(' ')[2])
    else:
      print('Could not find the results listed, most likely there is no stock information for some reason')
      # Check if a page refresh is in order, if it is, yield new request, else exit with error code giving debug reason
      needs_refresh = None #response.xpath('').get()
      if needs_refresh != None:
        # Indicates the page needs a refresh, let's initiate the same request.
        return scrapy.Request(response.url, self.parse)
      else:
        # We're not sure what the error is, further debugging may be necessary.
        # TODO: Log some kind of error message and stop the spider from running
        print('Some unknown error occurred')
        return []

    # Populate the number of stocks listed on the current page with the current sector
    for _ in range(maximum - minimum + 1):
      stocks.append(Stock(sector=sector))

    for i, ticker in enumerate(response.xpath('//tbody/tr/td[@aria-label="Symbol"]//text()').extract()):
      stocks[i]['ticker'] = ticker

    for i, name in enumerate(response.xpath('//tbody/tr/td[@aria-label="Symbol"]/a/@title').extract()):
      stocks[i]['name'] = name

    for i, intraday_price in enumerate(response.xpath('//tbody/tr/td[@aria-label="Price (Intraday)"]//text()').extract()):
      stocks[i]['intraday_price'] = intraday_price.replace(',','')

    for i, price_change in enumerate(response.xpath('//tbody/tr/td[@aria-label="Change"]//text()').extract()):
      stocks[i]['price_change'] = price_change.replace(',','')

    for i, percent_change in enumerate(response.xpath('//tbody/tr/td[@aria-label="% Change"]//text()').extract()):
      stocks[i]['percent_change'] = percent_change[:-1].replace(',','')

    for i, volume in enumerate(response.xpath('//tbody/tr/td[@aria-label="Volume"]//text()').extract()):
      volume = volume.replace(',','')
      stocks[i]['volume'] = str(float(volume[:-1]) * amt[volume[-1]]) if volume[-1] in amt.keys() else volume

    for i, avg_vol_3_month in enumerate(response.xpath('//tbody/tr/td[@aria-label="Avg Vol (3 month)"]//text()').extract()):
      if avg_vol_3_month == 'N/A':
        stocks[i]['avg_vol_3_month'] = None
      else:
        avg_vol_3_month = avg_vol_3_month.replace(',','')
        stocks[i]['avg_vol_3_month'] = str(float(avg_vol_3_month[:-1]) * amt[avg_vol_3_month[-1]]) if avg_vol_3_month[-1] in amt.keys() else avg_vol_3_month

    for i, market_cap in enumerate(response.xpath('//tbody/tr/td[@aria-label="Market Cap"]//text()').extract()):
      if market_cap == 'N/A':
        stocks[i]['market_cap'] = None
      else:
        market_cap = market_cap.replace(',','')
        stocks[i]['market_cap'] = str(float(market_cap[:-1]) * amt[market_cap[-1]]) if market_cap[-1] in amt.keys() else market_cap

    for i, pe_ratio_ttm in enumerate(response.xpath('//tbody/tr/td[@aria-label="PE Ratio (TTM)"]//text()').extract()):
      if pe_ratio_ttm == 'N/A':
        stocks[i]['pe_ratio_ttm'] = None
      else:
        pe_ratio_ttm = pe_ratio_ttm.replace(',','')
        stocks[i]['pe_ratio_ttm'] = str(float(pe_ratio_ttm[:-1]) * amt[pe_ratio_ttm[-1]]) if pe_ratio_ttm[-1] in amt.keys() else pe_ratio_ttm

    # Check if we have reached the last stock with the current filters
    if maximum < total:
      # If we have not, increase the offset by 100 and yield a new request for the next 100 stocks
      offset = offset + 100
      newUrl = re.sub('offset=\d+', 'offset=' + str(offset), response.url)
      yield scrapy.Request(newUrl, self.parse)

    # Submit the information on the current 100 stocks we are inspecting
    for stock in stocks:
      yield stock
