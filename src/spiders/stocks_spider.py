from __future__ import absolute_import
import scrapy
from time import sleep
import selenium 
from selenium import webdriver
from src.items import Stock
from scrapy import Selector
import re

class StocksSpider(scrapy.Spider):
  name = 'stocks'
  start_urls = [
    'https://finance.yahoo.com/screener/predefined/ms_healthcare?offset=0&count=100',
    # 'https://finance.yahoo.com/screener/predefined/ms_energy?offset=0&count=100',
    # 'https://finance.yahoo.com/screener/predefined/ms_technology?offset=0&count=100',
  ]

  def parse(self, response):
    self.driver = webdriver.Chrome('/Users/nickzarate/workspace/stocks/chromedriver')
    self.driver.get(response.url)
    filter_expand_button = self.driver.find_element_by_xpath('//*[@id="screener-criteria"]/descendant::button[contains(., "Edit")]')
    sleep(10)
    filter_expand_button.click()
    sleep(10)

    while True:
      remove_filter_buttons = self.driver.find_elements_by_xpath('//*[@id="screener-criteria"]/descendant::button[@data-test="remove-filter" and not(@title="Remove Sector")]')
      if len(remove_filter_buttons) == 0:
        break
      else:
        remove_filter_buttons[0].click()
      sleep(10)

    sleep(10)
    find_stocks_button = self.driver.find_element_by_xpath('//*[@id="screener-criteria"]/descendant::button[contains(., "Find Stocks")]')
    sleep(10)
    find_stocks_button.click()
    sleep(10)

    sector = re.search("ms_[^?]+", response.url).group()[3:]
    items = []
    amt = { 'k': 1000, 'M': 1000000, 'B': 1000000000, 'T': 1000000000000 }
    j = 0
    while j < 10000:
      ss = Selector(text = self.driver.page_source)

      res_count = ss.xpath('//div[@id="fin-scr-res-table"]/div[1]/div[1]/span[2]//text()').get()
      minimum, maximum, total = int(res_count.split('-')[0]), int(res_count.split('-')[1].split(' ')[0]), int(res_count.split('-')[1].split(' ')[2])

      for _ in range(maximum - minimum + 1):
        items.append(Stock(sector=sector))

      for i, ticker in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="Symbol"]//text()').extract()):
        items[i+j]['ticker'] = ticker

      for i, name in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="Name"]//text()').extract()):
        items[i+j]['name'] = name

      for i, intraday_price in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="Price (Intraday)"]//text()').extract()):
        items[i+j]['intraday_price'] = intraday_price.replace(',','')

      for i, price_change in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="Change"]//text()').extract()):
        items[i+j]['price_change'] = price_change.replace(',','')

      for i, percent_change in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="% Change"]//text()').extract()):
        items[i+j]['percent_change'] = percent_change[:-1].replace(',','')

      for i, volume in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="Volume"]//text()').extract()):
        volume = volume.replace(',','')
        items[i+j]['volume'] = str(float(volume[:-1]) * amt[volume[-1]]) if volume[-1] in amt.keys() else volume

      for i, avg_vol_3_month in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="Avg Vol (3 month)"]//text()').extract()):
        if avg_vol_3_month == 'N/A':
          items[i+j]['avg_vol_3_month'] = None
        else:
          avg_vol_3_month = avg_vol_3_month.replace(',','')
          items[i+j]['avg_vol_3_month'] = str(float(avg_vol_3_month[:-1]) * amt[avg_vol_3_month[-1]]) if avg_vol_3_month[-1] in amt.keys() else avg_vol_3_month

      for i, market_cap in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="Market Cap"]//text()').extract()):
        if market_cap == 'N/A':
          items[i+j]['market_cap'] = None
        else:
          market_cap = market_cap.replace(',','')
          items[i+j]['market_cap'] = str(float(market_cap[:-1]) * amt[market_cap[-1]]) if market_cap[-1] in amt.keys() else market_cap

      for i, pe_ratio_ttm in enumerate(ss.xpath('//*[@id="screener-results"]/descendant::tr/td[@aria-label="PE Ratio (TTM)"]//text()').extract()):
        if pe_ratio_ttm == 'N/A':
          items[i+j]['pe_ratio_ttm'] = None
        else:
          pe_ratio_ttm = pe_ratio_ttm.replace(',','')
          items[i+j]['pe_ratio_ttm'] = str(float(pe_ratio_ttm[:-1]) * amt[pe_ratio_ttm[-1]]) if pe_ratio_ttm[-1] in amt.keys() else pe_ratio_ttm

      if maximum >= total:
        break
      else:
        j = j + maximum - minimum + 1
        next_button = self.driver.find_element_by_xpath('//div[@id="scr-res-table"]//button[contains(., "Next")]')
        next_button.click()
        sleep(10)

    return items
