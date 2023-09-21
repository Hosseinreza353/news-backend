import json
from itemadapter import ItemAdapter

from news_crawl.items import NewsItem


class NewsCrawlPipeline:
    async def process_item(self, item: NewsItem, spider):
        print("-"*100)
        print(json.dumps(ItemAdapter(item).asdict()))
        # spider.settings.get("redis").publish(spider.settings.get("topic"), json.dumps(ItemAdapter(item).asdict()))
        print("+"*100)
