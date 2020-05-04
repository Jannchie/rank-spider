import os
from simpyder.spiders import AsynSpider
import pymongo
import datetime
url = 'https://s.weibo.com/top/summary?cate=realtimehot'

MONGO_URL = os.environ['MONGO_URL']
db = pymongo.MongoClient(MONGO_URL)


class WeiboHotSearchSpider(AsynSpider):
  def __init__(self):
    super().__init__(name="weibo spider", interval=3600, concurrency=1)

  def gen_url(self):
    while True:
      yield url

  async def parse(self, res):
    date = datetime.datetime.utcnow()
    data = res.xpath('/html/body/div[1]/div[2]/div[2]/table/tbody/tr')
    items = []
    for d in data:
      try:
        name = d.xpath('./td[2]/a/text()')[0]
        if len(d.xpath('./td[2]/span/text()')) == 0:
          continue
        value = int(d.xpath('./td[2]/span/text()')[0])
        if len(d.xpath('./td[3]/i/text()')) == 1:
          desc = d.xpath('./td[3]/i/text()')[0]
        else:
          desc = ''
        items.append([name, value, desc, date])
      except Exception as e:
        self.logger.exception(e)
      pass
    return items
    pass

  async def save(self, items):
    c = 0
    for item in items:
      db.weibo.hot.insert({
          'name': item[0],
          'value': item[1],
          'type': item[2],
          'date': item[3]})
      c += 1
    return c

    pass


if __name__ == "__main__":
  s = WeiboHotSearchSpider()
  s.run()
