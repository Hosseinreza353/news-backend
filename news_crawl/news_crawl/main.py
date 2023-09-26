import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from twisted.internet.asyncioreactor import install
install()

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy import spiderloader


settings = get_project_settings()
runner = CrawlerRunner(settings)

spider_loader = spiderloader.SpiderLoader.from_settings(settings)
for crawler in spider_loader.list():
    print(f"Running Spider {crawler:-^30}")
    runner.crawl(crawler)

d = runner.join()
d.addBoth(lambda _: reactor.stop())
reactor.run()
