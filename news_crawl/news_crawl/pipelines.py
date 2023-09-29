import asyncio
# import requests
from itemadapter import ItemAdapter

from news_crawl.spiders.mehr import MehrNewsSpider
from news_crawl.items import NewsItem


class NewsCrawlPipeline:
    # def __init__(self):
    #     self.max_topic_dts = {}

    # def open_spider(self, spider):
    #     if isinstance(spider, MehrNewsSpider):
    #         # print(await spider.redis.hgetall("last_news_dt"))
    #         print("radom log8", asyncio.run(spider.redis.hgetall("last_news_dt")))
    #         # spider.last_news_dt = asyncio.run(spider.redis.hgetall("last_news_dt"))

    async def process_item(self, item: NewsItem, spider):
        if isinstance(spider, MehrNewsSpider):
            # print("hasan", hasattr(spider, "redis"))
            # print("-"*100)
            # print(ItemAdapter(item).asdict())
            await spider.publish(ItemAdapter(item).asdict())
            # self.max_topic_dts.setdefault(item.category, "")
            # self.max_topic_dts[item.category] = max(item.time, self.max_topic_dts[item.category])
            # print("random log5", self.max_topic_dts)
            # resp = requests.post("http://localhost:8000/news/", json=ItemAdapter(item).asdict())
            # if resp.status_code == 201:
            #     spider.redis.sadd("seen_links", item.news_url)
            # else:
            #     print(resp.status_code)
            # print("+"*100)
            return item
    
    # def close_spider(self, spider):
    #     if isinstance(spider, MehrNewsSpider):
    #         # for topic, max_dt in self.max_topic_dts.items():
    #         #     await spider.redis.hset("last_news_dt", topic, max_dt)
    #         for k in self.max_topic_dts:
    #             if not self.max_topic_dts[k]:
    #                 del self.max_topic_dts[k]
    #         print("radom log6", "inserting to redis", len(self.max_topic_dts))
    #         if self.max_topic_dts:
    #             # asyncio.run(spider.update_last_news_dts(self.max_topic_dts))
    #             asyncio.get_event_loop().run_until_complete(spider.update_last_news_dts(self.max_topic_dts))
    #             # print(hgetall(spider.redis))
    #             # print(asyncio.run(spider.redis.hgetall("last_news_dt")))
    #             # print(asyncio.run(spider.redis.hset("last_news_dt", mapping=self.max_topic_dts)))
