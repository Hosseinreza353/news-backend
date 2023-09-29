from scrapy import Request, Spider, signals
from scrapy.http.response.html import HtmlResponse
from datetime import datetime as dt
import jdatetime as jdt
import itertools as it

from news_crawl.items import NewsItem
from news_crawl.mixin import RedisMixin

topics = {
    # "Society": 6,
    # 'Economy': 25,
    # 'markets': 653,
    # 'Sport': 9,
    'Politic': 7,
    'International': 8,
}
topics_fa_en = {
    "Society": "جامعه",
    'Economy': "اقتصاد",
    'markets': "بازار",
    'Sport': "ورزش",
    'Politic': "سیاست",
    'International': "بین الملل",
}


class MehrNewsSpider(RedisMixin, Spider):
    name = "mehrnews"
    last_news_dts = {}
    max_topic_dts = {}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MehrNewsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.item_scraped, signal=signals.item_scraped)
        return spider

    async def spider_opened(self, spider):
        last_news_dts = await spider.redis.hgetall("last_news_dts")
        spider.last_news_dts = last_news_dts
        spider.max_topic_dts = last_news_dts
        return spider
    
    async def spider_closed(self, spider, reason='finished'):
        if reason == 'finished':
            await spider.update_last_news_dts(spider.max_topic_dts)
            print(reason, 'spider closed')
    
    async def item_scraped(self, item, response, spider):
        # print(type(item), type(spider))
        spider.max_topic_dts.setdefault(item.category, "")
        spider.max_topic_dts[item.category] = max(item.time, spider.max_topic_dts[item.category])
        return response

    def start_requests(self):
        n = dt.utcnow()
        jn = jdt.date.fromgregorian(day=n.day, month=n.month, year=n.year)
        base_url = f"https://www.mehrnews.com/archive?pi=%d&tp=%d&ms=0&dy={jn.day}&mn={jn.month}&yr={jn.year}"
        for pi, (tp, tp_id) in it.product(range(3, 0, -1), topics.items()):
            url = base_url % (pi, tp_id)
            yield Request(url, callback=self.parse, meta={"topic": tp})

    async def parse(self, response: HtmlResponse):
        all_news = response.css("section#box517>div>ul>li.news")
        # TODO exception handling
        # all_times = all_news[0].css("time *::text").extract_first()
        # x = jdt.datetime.strptime(all_times[0], "%Y-%m-%d %H:%M")
        # x.togregorian()
        all_times = [
            news.css("time *::text").extract_first()
            for news in all_news
        ]
        all_times = [jdt.datetime.strptime(t, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M") for t in all_times][::-1]
        # print("random log2")
        all_anchors = [
            response.urljoin(news.css("div.desc>h3>a::attr(href)").extract_first())
            for news in all_news
        ][::-1]
        # print("random log4", len(all_times), len(all_anchors))
        all_anchors, all_times = await self.filter_news(all_anchors, all_times, response.meta.get("topic"))
        # print("random log1", len(all_times), len(all_anchors))
        for a, dt in zip(all_anchors, all_times):
            yield Request(
                a,
                callback=self.parse_news,
                cb_kwargs={"topic": response.meta.get("topic"), "dt": dt},
            )

    def parse_news(self, response: HtmlResponse, topic: str, dt: str):
        article = response.css("article#item")
        item_header = self.convert_text(article.css("div.item-header *::text").extract())
        item_summary = article.css("div.item-summary")
        thumbnail_url = item_summary.css(
            "figure.item-img img::attr(src)"
        ).extract_first()
        summary = self.convert_text(item_summary.css("p.summary *::text").extract())
        ps = article.css("div.item-body > div.item-text p")
        full_text = "\n".join([self.convert_text(p.css("*::text").extract()) for p in ps])
        yield NewsItem(
            publisher="mehrnews",
            header=item_header,
            abstract=summary,
            news_url=response.url,
            thumbnail_url=thumbnail_url,
            body=full_text,
            category=topic,
            time=dt,
            keywords=["Mehrnews", "مهرنیوز", topic, topics_fa_en.get(topic, topic)],
        )

    async def filter_news(self, links, times, topic):
        # return list(set(links).difference(set(await self.redis.smembers("seen_links"))))
        # print("random log7", self.last_news_dts)
        # last_dt = await self.redis.hget("last_news_dts", topic)
        # last_dt = "" if not last_dt else last_dt
        last_dt = self.last_news_dts.get(topic, "")
        zipped = list(zip(links, times))
        to_ret = [a_t for a_t in zipped if a_t[1] > last_dt]
        # print("random log3", len(to_ret))
        return [_[0] for _ in to_ret], [_[1] for _ in to_ret]

    def convert_text(self, str_list, det=" "):
        return det.join(str_list).replace("\r\n", "").replace("\n", "")
