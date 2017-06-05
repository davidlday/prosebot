# -*- coding: utf-8 -*-
from prosebot.items import Story
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import calendar
import dateutil.parser
import scrapy


class LightspeedSpider(CrawlSpider):

    name            = 'lightspeed'
    magazine_name   = 'Lightspeed Magazine'
    allowed_domains = ['lightspeedmagazine.com']
    start_urls      = [
        'http://www.lightspeedmagazine.com/category/fiction/fantasy/',
        'http://www.lightspeedmagazine.com/category/fiction/science-fiction/'
    ]
    content_xpath   = '//*[@id="content"]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=([
                    '/category/fiction/fantasy/',
                    '/category/fiction/fantasy/page/\d{1,}/',
                    '/category/fiction/science-fiction/',
                    '/category/fiction/science-fiction/page/\d{1,}/',
                ]),
                restrict_xpaths=(content_xpath)
            )
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=([
                    '/fiction/.+'
                ]),
                deny=([
                    '/category/.*',
                    '/authors/.*',
                    '/nonfiction/.*',
                    '/issues/.*',
                    '/ebooks/.*',
                    '/subscribe/.*',
                ]),
                restrict_xpaths=(content_xpath)
            ), callback='parse_story'
        ),
    )


    def parse_story(self, response):
        base_xpath      = '//div[@id="content"]//div[re:test(@id,"post-\d+")]'
        story_post      = response.xpath(base_xpath)
        text            = ''
        request_headers = response.request.headers
        referer_url     = request_headers.get('Referer', None).decode(request_headers.encoding)
        genre           = referer_url.split('/')[5].replace('-', ' ')

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = [genre]
        story['original_tags'] = []
        story['url']    = response.url
        story['title']  = ' '.join(story_post.xpath('.//h1[contains(@class,"posttitle")]/text()').extract())
        story['author'] = story_post.xpath('.//p[@class="postmetadata"]/a/text()').extract()

        # Extract Published Month / Year
        meta_pub_date = dateutil.parser.parse(story_post.xpath('/html/head/meta[contains(@property, "article:published_time")]/@content').extract()[0])
        story['pub_year'] = str(meta_pub_date.year)
        pub_month_no = "%02d" % meta_pub_date.month
        story['pub_month'] = calendar.month_name[meta_pub_date.month].lower()
        story['pub_date'] = story['pub_year'] + '-' + pub_month_no + '-01'

        # Extract the body of the story
        story_lines = [''.join(p.xpath('.//text()').extract())
                for p in story_post.xpath('.//div[contains(@class, "entry-content")]/p')]
        story['text']   = "\n".join(story_lines)

        yield story

