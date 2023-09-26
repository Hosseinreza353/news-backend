import requests
from itemadapter import ItemAdapter

from news_crawl.items import NewsItem


class NewsCrawlPipeline:
    async def process_item(self, item: NewsItem, spider):
        # print("hasan", hasattr(spider, "redis"))
        # print("-"*100)
        # print(ItemAdapter(item).asdict())
        # spider.redis.publish(ItemAdapter(item).asdict())
        resp = requests.post("http://localhost:8000/news/", json=ItemAdapter(item).asdict())
        if resp.status_code == 201:
            spider.redis.sadd("seen_links", item.news_url)
        else:
            print(resp.status_code)
        # print("+"*100)
