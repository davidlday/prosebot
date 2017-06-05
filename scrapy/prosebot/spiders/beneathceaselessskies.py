# -*- coding: utf-8 -*-
import scrapy
import re
import calendar
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class BeneathCeaselessSkiesSpider(CrawlSpider):
    name            = 'beneathceaselessskies'
    magazine_name   = 'Beneath Ceaseless Skies'
    allowed_domains = ['beneath-ceaseless-skies.com']
    start_urls      = ['http://www.beneath-ceaseless-skies.com/stories/']
    content_xpath   = '//td[@id="content_cell"]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=(
                    '/stories/page/\d{1,}/'
                ),
                restrict_xpaths=(content_xpath)
            )
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=(
                    '/stories/.+'
                ),
                deny=(
                    '/stories/page/\d{1,}/',
                    '/current-issue/',
                    '/issues/.+',
                    '/list-of-authors/',
                    '/next-issue/',
                    '/audio/.*',
                    '/audio-vault/.*',
                    '/feed/.*',
                    '/artwork/',
                    '/subscribe/.*',
                    '/the-bcs-anthologies/.*',
                    '/news/.*',
                    '/category/.*',
                    '/about-us/.*',
                    '/submissions/',
                    '/banners-and-covers/',
                    '/\?am_force_theme_layout=mobile',
                    '/contact/',
                    '/support-bcs/.*',
                    '/authors/.*',
                ),
                restrict_xpaths=(content_xpath)
            ), callback='parse_story'
        ),
    )

    def parse_story(self, response):
        base_xpath      = '//td[@id="content_cell"]'
        story_post      = response.xpath(base_xpath)
        text            = ''

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = ['fantasy']
        story['url']    = response.url
        # No original_tags on this site
        story['original_tags'] = []
        story['title']  = story_post.xpath('.//div[@class="post_title"]/a/text()').extract()
        story['author'] = []
        auth_lines = [auth_line.replace(u'\u2014','').strip() for auth_line in story_post.xpath('.//span[@class="post_author"]/a//text()').extract()]
        for auth_line in auth_lines:
            for author in auth_line.split(' & '):
                story['author'].append(author)

        # Extract Published Month / Year
        month_name_no = dict((v.lower(),"%02d" % k) for k,v in enumerate(calendar.month_name))
        post_date = story_post.xpath('.//span[@class="post_date"]/text()').extract()[0].replace(',', '').strip().lower()
        [story['pub_month'], pub_day, story['pub_year']] = post_date.split()
        pub_day = "%02d" % int(pub_day)
        story['pub_date'] = story['pub_year'] + '-' + month_name_no[story['pub_month']] + '-' + pub_day

        # Extract the body of the story
        story_lines = [''.join(p.xpath('.//text()').extract())
                for p in story_post.xpath('.//div[@class="bcs_story_content"]/p')]
        story['text']   = "\n".join(story_lines)

        yield story
