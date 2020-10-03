import ssl
import os
from simpyder.spiders import AsynSpider
from simpyder import Spider, FAKE_UA, SimpyderConfig
import pymongo
import datetime
import asyncio
url = 'https://s.weibo.com/top/summary?cate=realtimehot'

ssl._create_default_https_context = ssl._create_unverified_context
BILIOB_MONGO_URL = os.environ['BILIOB_MONGO_URL']
db = pymongo.MongoClient(BILIOB_MONGO_URL)


class WeiboHotSearchSpider(AsynSpider):

  async def gen_url(self):
    while True:
      yield url
      await asyncio.sleep(20)

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

  async def save(self, items):
    c = 0
    for item in items:
      db.weibo.hot.insert_one({
          'name': item[0],
          'value': item[1],
          'type': item[2],
          'date': item[3]})
      c += 1
    return c


if __name__ == "__main__":
  s = WeiboHotSearchSpider(
      name="weibo spider", user_agent=FAKE_UA, interval=60 * 30, concurrency=1)
  s.run()
