import pymongo
from simpyder import Spider, FAKE_UA, SimpyderConfig
from datetime import datetime
import os
MONGO_URL = os.environ['MONGO_URL']
db = pymongo.MongoClient()


class HotSearchSpider(Spider):
  def gen_url(self):
    while True:
      yield "https://www.zhihu.com/billboard"

  def parse(self, response):
    data = response.xpath('//div[@class="HotList-itemBody"]')
    date = datetime.utcnow()
    items = []
    for d in data:
      try:
        title = d.xpath('div[@class="HotList-itemTitle"]/text()')[0]
        value = int(d.xpath(
            'div[@class="HotList-itemMetrics"]/text()')[0].rstrip('万热度'))
        items.append([title, value, date])
      except Exception as e:
        self.logger.exception(e)
    return items

  def save(self, item):
    for e in item:
      db.zhihu.hot.insert_one({
          'title': e[0],
          'value': e[1],
          'date': e[2]
      })
    return e


if __name__ == "__main__":
  s = HotSearchSpider("知乎热搜")
  sc = SimpyderConfig()
  sc.COOKIE = FAKE_UA
  sc.DOWNLOAD_INTERVAL = 15 * 60
  sc.PARSE_THREAD_NUMER = 1
  s.set_config(sc)
  s.run()
