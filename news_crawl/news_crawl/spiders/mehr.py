from scrapy import Request, Spider
from scrapy.http.response.html import HtmlResponse
from datetime import datetime as dt
import jdatetime as jdt
import itertools as it

from news_crawl.items import NewsItem
from news_crawl.mixin import RedisMixin

topics = {
    "Society": 6,
    'Economy': 25,
    'markets': 653,
    'Sport': 9,
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

    def start_requests(self):
        n = dt.utcnow()
        jn = jdt.date.fromgregorian(day=n.day, month=n.month, year=n.year)
        self.expire_seen_links()
        base_url = f"https://www.mehrnews.com/archive?pi=%d&tp=%d&ms=0&dy={jn.day}&mn={jn.month}&yr={jn.year}"
        for pi, (tp, tp_id) in it.product(range(3), topics.items()):
            url = base_url % (pi + 1, tp_id)
            yield Request(url, callback=self.parse, meta={"topic": tp})

    def parse(self, response: HtmlResponse):
        all_news = response.css("section#box517>div>ul>li.news")
        all_anchors = [
            response.urljoin(news.css("div.desc>h3>a::attr(href)").extract_first())
            for news in all_news
        ]
        all_anchors = self.filter_non_existing_news(all_anchors)
        for a in all_anchors:
            yield Request(
                a,
                callback=self.parse_news,
                cb_kwargs={"topic": response.meta.get("topic")},
            )

    def parse_news(self, response: HtmlResponse, topic: str):
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
            keywords=["Mehrnews", "مهرنیوز", topic, topics_fa_en.get(topic, topic)],
        )

    def filter_non_existing_news(self, links):
        return list(set(links).difference(set(self.redis.smembers("seen_links"))))

    def expire_seen_links(self):
        # TODO
        pass

    def convert_text(self, str_list, det=" "):
        return det.join(str_list).replace("\r\n", "").replace("\n", "")
