# -*- coding: utf-8 -*-
import scrapy
import calendar
import re
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class ApexSpider(CrawlSpider):
    name            = 'apex'
    magazine_name   = 'Apex Magazine'
    magazine_genre  = ['fantasy', 'horror', 'science fiction']
    allowed_domains = ['apex-magazine.com']
    start_urls      = ['http://www.apex-magazine.com/category/short-fiction/']
    content_xpath   = '//*[@id="left-area"]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=([
                    '/category/short-fiction/',
                    '/category/short-fiction/page/\d{1,}/'
                ]),
                restrict_xpaths=(content_xpath)
            )
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                deny=(
                    '/category/short-fiction/',
                    '/category/short-fiction/page/\d{1,}/'
                    '/clavis-aurea/',
                    '/issue-.*',
                    '/backissues/',
                    '/back-issues-.*',
                    '/support-us',
                    '/apex-magazine-podcast/',
                    '/about-apex-magazine/',
                    '/digital-reader-apps/',
                    '/masthead-2/',
                    '/submission-guidelines/',
                    '/advertising/',
                    '/our-authors/',
                    '/awards-and-nominations/',
                    '/contact-2/',
                    '/story-of-the-year/',
                    '/category/.*',
                    '/tag/.*',
                    '/author/.*',
                    '/feed/',
                ),
                restrict_xpaths=(content_xpath)
            ), callback='parse_story'),
        )

    def parse_story(self, response):
        base_xpath      = '//*[@id="content-area"]'
        story_post      = response.xpath(base_xpath)
        text            = ''

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = self.magazine_genre
        story['url']    = response.url
        story['original_tags'] = story_post.xpath('.//div[@id="tags"]/a/text()').extract()
        story['title']  = story_post.xpath('.//*[@id="category-name"]/h1[@class="category-title"]/text()').extract()[0]
        story['author'] = story_post.xpath('.//*[@id="category-name"]/p[@class="description"]/a[@rel="author"]/text()').extract()

        # Extract Published Month / Year
        story['pub_date'] = response.xpath('.//meta[@property="article:published_time"]/@content').extract()[0].split('T')[0]
        [story['pub_year'], pub_month_no, pub_day] = story['pub_date'].split('-')
        story['pub_month'] = calendar.month_name[int(pub_month_no)].lower()

        # Extract the body of the story
        story_lines = [''.join(p.xpath('.//text()').extract())
                for p in story_post.xpath('.//*[@id="left-area"]/div[contains(@class,"post")]/p')]
        story['text']   = "\n".join(story_lines)

        yield story
