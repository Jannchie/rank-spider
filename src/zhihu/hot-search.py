import pymongo
from simpyder import FAKE_UA, SimpyderConfig
from simpyder.spiders import AsynSpider
from datetime import datetime
import os
MONGO_URL = os.environ['MONGO_URL']
db = pymongo.MongoClient()


class HotSearchSpider(AsynSpider):
  async def gen_url(self):
    while True:
      yield "https://www.zhihu.com/billboard"

  async def parse(self, response):
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

  async def save(self, item):
    for e in item:
      try:
        db.zhihu.hot.insert_one({
            'title': e[0],
            'value': e[1],
            'date': e[2]
        })
      except Exception as e:
        self.logger.exception(e)
    return len(item)


if __name__ == "__main__":
  s = HotSearchSpider(name="zhihu spider", user_agent=FAKE_UA,
                      interval=60 * 30, concurrency=1)
  s.run()
