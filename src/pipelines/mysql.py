from __future__ import absolute_import
from mysql import connector
from creds import Creds

class MySQLPipeline(object):
  def __init__(self):
    self.host = Creds.host
    self.user = Creds.user
    self.passwd = Creds.passwd

  def open_spider(self, spider):
    print('setting up database...')
    self.db = connector.connect(host=self.host, user=self.user, passwd=self.passwd)
    print('setting up cursor...')
    self.cursor = self.db.cursor()
    self.cursor.execute('USE investments')

  def close_spider(self, spider):
    self.db.commit()
    print('closing cursor...')
    self.cursor.close()
    print('closing database...')
    self.db.close()

  def process_item(self, item, spider):
    sql = "INSERT INTO stocks (ticker, name, intraday_price, price_change, percent_change, volume, avg_vol_3_month, market_cap, pe_ratio_ttm, sector) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (item['ticker'], item['name'], item['intraday_price'], item['price_change'], item['percent_change'], item['volume'], item['avg_vol_3_month'], item['market_cap'], item['pe_ratio_ttm'], item['sector'])
    self.cursor.execute(sql, val)
    
    return item
