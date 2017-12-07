# -*- coding: utf-8 -*-
import re
from unicodedata import normalize

from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class DocumentationSpider(CrawlSpider):
    name = 'documentation'
    allowed_domains = ['docs.wso2.com']

    doc_urls = [
        'AM210',
        'ApiCloud',
        'EI611',
        'EIP',
        'IntegrationCloud',
        'IS530',
        'IdentityCloud',
        'DAS310',
        'IOTS310',
        'DeviceCloud',
        'OpenBanking',
        'KA100',
        'MA100',
        'PM210',
        'DF120',
        'ESBCONNECTORS',
        'ISCONNECTORS',
        'ANALYTICSEXTENSIONS',
        'SIDDHIEXTENSIONS',
        'ManagedCloud',
        'Governance540',
        'ADMIN44x',
        'CLUSTER44x',
        'AS530',
        'GS140',
        'AF210',
        'CG100',
        'PP411',
        'CARBON4411',
        'MB320',
        'APPM120',
        'ES210',
        'DVS380'
    ]

    # Since FAQ pages are not crawled by the crawler they have to be given explicitly
    faq_urls = [url + '/FAQ' for url in doc_urls]

    start_urls = [str('https://docs.wso2.com/display/' + p) for p in doc_urls + faq_urls]
    # start_urls = ['https://docs.wso2.com/display/IS530/User+Account+Locking+and+Account+Disabling']
    re_allowed = r'.*com\/display\/(%s).*' % '|'.join(doc_urls + faq_urls)

    rules = [Rule(LinkExtractor(allow=[re_allowed]), callback="parse_item", follow=True)]

    @staticmethod
    def parse_item(response):
        """Scraping the relevant web page and obtaining contents of titles, headers(imp1), hyperlinks and bold characters
        (imp2) and plain text"""
        print '\033[94m'
        print('Processing..' + response.url)
        print '\033[0m',

        try:
            html = response.xpath("//div[@id='main-content'and @class='wiki-content']").extract_first().strip()
        except AttributeError:
            # Passing the urls which don't have the specified page format
            return

        # Making non-decodable ascii codecs into decodable
        clean_html = normalize('NFKD', u'%s' % html).encode('ascii', 'ignore').decode('ascii', 'ignore')

        # Placing periods(.) after the <td>, <li>, <p>, <br>, <ul> and <br> html tags
        formatting_html = re.sub(r'(<\/((td)|(li)|(p)|(br))>)', r'.\1', clean_html)
        formatted_html = re.sub(r'(<((ul)|(ol)).+?>)', r'.\1', formatting_html)
        tree = Selector(text=formatted_html)

        scrape_result = {
            '_id': str(response.url).split('?', 1)[0],
            'title': response.xpath("//h1[@id='title-text']//*/text()").extract_first(),
            'imp1': response.xpath(
                "//div[@id='main-content'and @class='wiki-cont"
                "ent']//*/text()[not(ancestor::div[contains(@class,"
                "'code panel') or contains(@class,'expand-container')] or ancestor::code or ancestor::pre) and ( "
                "ancestor::h1 or ancestor::h2 or ancestor::h3 or ancestor::h4 "
                "or ancestor::h5 or ancestor::th)]").extract(),
            'imp2': response.xpath(
                "//div[@id='main-content'and @class='wiki-content']//*/text()[not(ancestor::div[contains(@class,"
                "'code panel') or contains(@class,'expand-container')] or ancestor::code or ancestor::pre) and ( "
                "ancestor::strong or ancestor::a)]").extract(),
            'plain': tree.xpath(
                "//div[@id='main-content'and @class='wiki-content']//*/text()[not(ancestor::div[contains(@class,"
                "'code panel') or contains(@class,'expand-container')] or ancestor::code or ancestor::pre) and not( "
                "ancestor::h1 or ancestor::h2 or ancestor::h3 or ancestor::h4 "
                "or ancestor::h5 or ancestor::th)]").extract(),

        }

        yield scrape_result
