import scrapy

class StocksSpider(scrapy.Spider):
  name = 'stocks'
  start_urls = [
    'https://finance.yahoo.com/sector/ms_healthcare',
    'https://finance.yahoo.com/sector/ms_energy',
    'https://finance.yahoo.com/sector/ms_technology',
  ]

  def parse(self, response):
    # Parse through stocks
    page = response.url.split('/')[-1]
    filename = '%s.html' % page

    with open(filename, 'wb') as f:
      f.write(response.body)
    self.log('Saved file %s' % filename)
