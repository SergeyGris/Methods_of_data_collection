from lxml import html
import requests
import pandas as pd

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
URL_YANDEX_NEWS = 'https://yandex.ru/news/'
URL_LENTA_NEWS = 'https://lenta.ru/'

headers = {
    'User-Agent': USER_AGENT,
}

params = {
    'sso_failed': '',
}


def get_content_dom_from_html_text(url, headers=None, params=None):
    response = requests.get(url, headers=headers, params=params)
    content_dom = html.fromstring(response.text)

    print(response.url)

    return content_dom


def parser_yandex_news(content_dom):
    news_container = content_dom.xpath("//section//div[contains(@class, 'mg-grid')]")
    yandex_news = []
    for new_container in news_container:
        new_source = new_container.xpath(".//div[@class='mg-card-footer__left']//a/text()")[0]
        new_text = new_container.xpath(".//h2/a/text()")[0].replace('\xa0', ' ')
        new_link = new_container.xpath(".//h2/a/@href")[0]
        new_date = new_container.xpath(".//span[@class='mg-card-source__time']/text()")[0]
        news_dict = {
            'new_source': new_source,
            'new_text': new_text,
            'new_link': new_link,
            'new_date': new_date,
        }
        yandex_news.append(news_dict)

    return yandex_news


def parser_lenta_news(content_dom):
    news_container = content_dom.xpath("//a[contains(@class, 'card-')]")
    lenta_news = []
    for new_container in news_container:
        new_source = new_container.xpath(".//*[name()='news']/*[name()='use']/attribute::*")
        if len(new_source) == 1:
            new_source = new_source[0].split('ui-label_')
            if len(new_source) == 2:
                new_source = new_source[1]
            else:
                new_source = 'Lenta.ru'
        else:
            new_source = 'Lenta.ru'
        new_text = new_container.xpath(".//span[contains(@class, 'card-')]/text()")
        if len(new_text) == 1:
            new_text = new_text[0]
        else:
            new_text = None
        new_link = URL_LENTA_NEWS + new_container.xpath("./@href")[0]

        new_date = new_container.xpath(".//time/text()")
        if len(new_date) == 1:
            new_date = new_date[0]
        else:
            new_date = None
        news_dict = {
            'new_source': new_source,
            'new_text': new_text,
            'new_link': new_link,
            'new_date': new_date,
        }
        lenta_news.append(news_dict)

    return lenta_news


def get_news(content_dom, parser_name):
    result = None

    if parser_name == 'yandex':
        result = parser_yandex_news(content_dom)
    elif parser_name == 'lenta':
        result = parser_lenta_news(content_dom)

    return result


dom = get_content_dom_from_html_text(URL_YANDEX_NEWS, headers=headers, params=params)
yandex_news = get_news(dom, 'yandex')

print(pd.DataFrame(yandex_news))

dom = get_content_dom_from_html_text(URL_LENTA_NEWS, headers=headers, params=params)
lenta_news = get_news(dom, 'lenta')

print(pd.DataFrame(lenta_news))
