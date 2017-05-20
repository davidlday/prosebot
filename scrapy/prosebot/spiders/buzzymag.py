# -*- coding: utf-8 -*-
import scrapy
import re
import calendar
from prosebot.items import Story
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class BuzzymagSpider(CrawlSpider):
    name            = "buzzymag"
    allowed_domains = ["buzzymag.com"]
    start_urls      = ["http://buzzymag.com/category/original-fiction/"]
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(allow=('/category/original-fiction/page/\d{1,}/'))),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=(
                    '/.+'
                ),
                deny=(
                    '/about/',
                    '/contact/',
                    '/submissions/',
                    '/category/news/',
                    '/category/reviews/.*',
                    '/category/interviews/.*',
                    '/category/original-fiction/.*',
                    '/the-best-of-buzzy-mag-\d{4}',
                    '/contests-prizes/',
                    '/category/general-musings/.*',
                    '/author/.*',
                    '/interview-clark-gregg-marvels-agents-shield/',
                    '/.+-interview/',
                    '/.+-book-review/',
                    '/.+-blog-.+/',
                )
            ), callback='parse_story'
        ),
    )

    def parse_story(self, response):
        base_xpath      = '//*[re:test(@id,"^post-\d*$")]'
        story_post      = response.xpath(base_xpath)
        text            = ''

        story           = Story()
        story['magazine'] = "Buzzy Mag"
        story['genre']  = ['fantasy', 'horror', 'science fiction']
        story['original_tags'] = story_post.xpath('.//span[@class="thecategory"]/a/text()').extract()
        story['url']    = response.url
        story['title'] = ' '.join(story_post.xpath('.//h1[contains(@class,"title")]/text()').extract())
        story['author'] = story_post.xpath('.//span[@class="theauthor"]/a/text()').extract()

        # Extract Published Month / Year
        month_name_no = dict((v.lower(),"%02d" % k) for k,v in enumerate(calendar.month_name))
        the_time = story_post.xpath('.//span[@class="thetime"]/text()').extract()[0].split()
        story['pub_month'] = the_time[1].lower()
        story['pub_year'] = the_time[3]
        pub_day = "%02d" % int(re.sub(r'\D*$', '', the_time[2]))
        story['pub_date'] = story['pub_year'] + '-' + month_name_no[story['pub_month']] + '-' + pub_day

        # Extract the body of the story
        story_lines = [p.strip() for p in story_post.xpath('.//div[contains(@class,"post-single-content")]/p/text()').extract()]
        story['text']   = "\n".join(story_lines)

        yield story
