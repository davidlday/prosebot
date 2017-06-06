# -*- coding: utf-8 -*-
import scrapy
import re
import calendar
import dateutil.parser
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class UncannySpider(CrawlSpider):
    name            = 'uncanny'
    magazine_name   = 'Uncanny Magazine'
    magazine_genre  = ['fantasy','science fiction']
    allowed_domains = ['uncannymagazine.com']
    start_urls      = [
        'http://uncannymagazine.com/type/fiction/',
    ]
    content_xpath   = '//main[@class="archive_main"]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=([
                    '/type/fiction/',
                    '/type/fiction/page/\d{1,}/',
                ]),
                restrict_xpaths=(content_xpath)
            )
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=([
                    '/article/.+/',
                ]),
                deny=([
                    '/type/fiction/page/\d{1,}/',
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
    issue_dates = {}
    issue_date_pattern = re.compile(
        r'\s(?:%s)\s\d{1,2},\s\d{4}' % '|'.join(calendar.month_name[1:])
    )

    def parse_story(self, response):
        base_xpath      = '//main[@class="main"]/article[re:test(@id,"post-\d+")]'
        story_post      = response.xpath(base_xpath)
        text            = ''

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = self.magazine_genre
        # No original_tags on this site
        story['original_tags'] = []
        story['url']    = response.url
        story['title']  = ' '.join(story_post.xpath('./h2[contains(@class,"entry-title")]//text()').extract())
        story['author'] = story_post.xpath('./h4[@class="byline"]/a/text()').extract()

        # Extract the body of the story
        story_lines = [''.join(p.xpath('.//text()').extract())
                for p in story_post.xpath('.//div[contains(@class, "entry-content")]/p[re:test(@class,"p[1-3]")]')]
        story['text']   = "\n".join(story_lines)

        # Derive publication date from issue page
        # See: https://stackoverflow.com/questions/33589136/scrapy-understanding-how-do-items-and-requests-work-between-callbacks#33590207
        issue_url = response.xpath(
            '//aside/div[@class="widget"]/div[@class="featured_issue_thumbnail"]/a/@href'
        ).extract()[0]
        issue_request = scrapy.Request(
            issue_url, callback=self.parse_issue_date
        )
        issue_request.meta['story'] = story

        yield issue_request

    # Uncanny doesn't provide dates for each story, but does link to the issue,
    # which in turns has an availability date in the first paragraph.
    # Build a list of issue URLs and corresponding publication date.
    # See: https://doc.scrapy.org/en/latest/topics/request-response.html#passing-additional-data-to-callback-functions
    def parse_issue_date(self, response):
        story = response.meta['story']
        if response.url not in self.issue_dates:
            date_text = [' '.join(p.xpath('.//text()').extract())
                for p in response.xpath(
                    '//main[@class="issue_main"]//div[@class="issue_content"]/p'
                )]
            match = self.issue_date_pattern.search(' '.join(date_text))
            if not match:
                self.logger.error("No match %s", self.issue_date_pattern)
            else:
                self.issue_dates[response.url] = dateutil.parser.parse(match[0].strip())
        # Set date based on issue
        meta_pub_date = self.issue_dates[response.url]
        story['pub_year'] = str(meta_pub_date.year)
        pub_month_no = "%02d" % meta_pub_date.month
        pub_day_no =  "%02d" % meta_pub_date.day
        story['pub_month'] = calendar.month_name[meta_pub_date.month].lower()
        story['pub_date'] = story['pub_year'] + '-' + pub_month_no + '-' + pub_day_no

        yield story

