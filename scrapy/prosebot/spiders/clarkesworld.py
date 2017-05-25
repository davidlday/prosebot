import scrapy
import re
import calendar
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class ClarkesworldSpider(CrawlSpider):
    name            = 'clarkesworld'
    magazine_name   = 'Clarkesworld'
    allowed_domains = ['clarkesworldmagazine.com']
    start_urls      = ['http://clarkesworldmagazine.com/category/Fiction/']
    content_xpath   = '//div[@class="story-frame"]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=([
                    '/category/Fiction/page/\d{1,}/'
                ]),
                restrict_xpaths=(content_xpath)
            )
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=([
                    '/.+_\d{2}_\d{2}/'
                ]),
                deny=([
                    '/category/Fiction/page/\d{1,}/',
                    '/audio_\d{2}_\d{2}.*/',
                    '/issue_\d{1,}',
                    '/author/.+',
                    '/category/Fiction/.*',
                    '/.*\.mp3',
                ]),
                restrict_xpaths=(content_xpath)
            ), callback='parse_story'
        ),
    )


    def parse_story(self, response):
        base_xpath      = '//div[contains(@class, "interior_body_1")]'
        story_post      = response.xpath(base_xpath)
        text            = ''

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = ['science fiction','fantasy']
        # No tags on stories.
        story['original_tags'] = []
        story['url']    = response.url
        story['title']  = ' '.join(story_post.xpath('.//p[contains(@class, "story-title")]/text()').extract())
        story['author'] = []
        auth_lines = [auth_line.replace(u'\u2014','').strip() for auth_line in story_post.xpath('.//p[contains(@class, "story-author")]/text()').extract()]
        for auth_line in auth_lines:
            for author in auth_line.split(' and '):
                story['author'].append(author)

        # Extract Published Month / Year
        month_name_no = dict((v.lower(),"%02d" % k) for k,v in enumerate(calendar.month_name))
        [issue, pub_date_str] = response.xpath('//p[contains(@class,"issue")]/a/text()').extract()[0].split(',')
        [story['pub_month'], story['pub_year']] = pub_date_str.strip().lower().split(' ')
        story['pub_date'] = story['pub_year'] + '-' + month_name_no[story['pub_month']] + '-01'

        # Extract the body of the story
        story_lines = [''.join(p.xpath('.//text()').extract())
                for p in story_post.xpath('.//div[@class="story-text"]/p')]
        story['text']   = "\n".join(story_lines)

        yield story
