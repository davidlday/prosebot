# -*- coding: utf-8 -*-
import scrapy
import re
import calendar
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class DailyScienceFictionSpider(CrawlSpider):
    name            = 'dailysciencefiction'
    magazine_name   = 'Daily Science Fiction'
    allowed_domains = ['dailysciencefiction.com']
    start_urls      = ['http://dailysciencefiction.com/month']
    content_xpath   = '//*[@id="mainBodyContent"]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=([
                    '/month/stories/\d{4}\.\d{2}'
                ]),
                restrict_xpaths=(content_xpath)
            )
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=([
                    '/story/.+'
                ]),
                deny=([
                    '/month',
                    '/genre/.+'
                ]),
                restrict_xpaths=(content_xpath)
            ), callback='parse_story'
        ),
    )

    def parse_story(self, response):
        base_xpath      = '//*[@id="mainBodyContent"]'
        story_post      = response.xpath(base_xpath)
        text            = ''

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = ['science fiction']
        story['url']    = response.url
        # Tags are embedded in the URL, but not actually displayed on the story's page.
        # Use set and list to ensure a list of unique values
        story['original_tags'] = list(set(response.url.split('/')[3:5]))
        story['title']  = story_post.xpath('.//h1/text()').extract()[0].strip()
        story['author'] = []
        for byline in story_post.xpath('.//div[@class="storyAuthor"]/text()').extract():
            for auth in byline.replace('by ', '').split(','):
                story['author'].append(re.sub(r'\s\s+', ' ', auth.strip()))

        # Extract publication date
        month_name_no = dict((v.lower(),"%02d" % k) for k,v in enumerate(calendar.month_name))
        [pub_date_text, pub_month_dayth, pub_year] = story_post.xpath('.//div[@id="publicationDate"]/text()').extract()[0].split(',')
        [pub_month_name, pub_dayth] = pub_month_dayth.strip().split(' ')
        story['pub_month'] = pub_month_name.strip().lower()
        story['pub_year'] = pub_year.strip()
        pub_day = "%02d" % int(re.sub(r'\D*$', '', pub_dayth))
        story['pub_date'] = story['pub_year'] + '-' + month_name_no[story['pub_month']] + '-' + pub_day

        # Extract the body of the story
        story_lines = [''.join(p.xpath('.//text()').extract())
                for p in story_post.xpath('.//div[contains(@class, "storyText")]')]
        story['text']   = "\n".join(story_lines)

        yield story
