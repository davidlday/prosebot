# -*- coding: utf-8 -*-
import scrapy
import re
import calendar
import dateutil.parser
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class NewYorkerSpider(CrawlSpider):
    name            = 'newyorker'
    magazine_name   = 'The New Yorker'
    magazine_genre  = ['general']
    archives_start_page = 0
    allowed_domains = ['newyorker.com']
    start_urls      = ['http://www.newyorker.com/magazine/fiction/']
    content_xpath   = '//*[@id="main"]//section[contains(@class,"main-content")]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=([
                    '/magazine/fiction/',
                    '/magazine/fiction/page/\d{1,}/',
                ]),
                restrict_xpaths=(content_xpath)
            ),
            process_links='check_archives_page'
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=([
                    '/magazine/\d{4}/\d{2}/\d{2}/.+',
                ]),
                deny=([
                    '/magazine/fiction/',
                    '/magazine/fiction/page/\d{1,}/',
                    '/contributors/.*',
                ]),
                restrict_xpaths=(content_xpath)
            ), callback='parse_story'
        ),
    )

    # They have stories going way back. Older stuff is readable only via
    # http://archives.newyorker.com, which is only detectable once on the page.
    def check_archives_page(self, links):
        if self.archives_start_page > 0:
            for link in links:
                page = link.split('/')[-1]
                try:
                    if int(page) >= self.archives_start_page:
                        links.remove(link)
                except ValueError:
                    self.logger.warn("Invalid page number %s parsed from %s", page, link)
        return links

    def parse_story(self, response):
        base_xpath      = '//*[@itemid="' + response.url + '"]'
        story_post      = response.xpath(base_xpath)
        text            = ''
        referer_url     = request_headers.get('Referer', None).decode(request_headers.encoding)
        referer_page    = referer_url.split('/')[-1]

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = self.magazine_genre
        story['original_tags'] = response.xpath('//meta[@property="article:tag"]/@content').extract()
        story['url']    = response.url
        story['title']  = response.xpath('//meta[@property="og:title"]/@content').extract()
        story['author'] = story_post.xpath('.//*[@id="masthead"]//a[@rel="author"]//text()').extract()

        # Extract Published Month / Year
        meta_pub_date = dateutil.parser.parse(story_post.xpath('//meta[@name="pubdate"]/@content').extract()[0])
        story['pub_year'] = str(meta_pub_date.year)
        pub_month_no = "%02d" % meta_pub_date.month
        pub_day_no = "%02d" % meta_pub_date.day
        story['pub_month'] = calendar.month_name[meta_pub_date.month].lower()
        story['pub_date'] = story['pub_year'] + '-' + pub_month_no + '-' + pub_day_no

        # Check if it's an archived story. Will have a link to read the archived
        # story
        archive_lnks = response.xpath(
            '//*[@id="articleBody"]//a[re:test(@href,"http://archives.newyorker.com/")]')
        if len(archive_lnks) > 0:
            # Leave text empty if it is. Story will get dropped in pipeline.
            self.logger.info("Found archive links. Skipping %s", response.url)
        else:
            # Extract the body of the story
            story_lines = [''.join(p.xpath('.//text()').extract())
                    for p in story_post.xpath('.//*[@id="articleBody"]//p')]
            story['text']   = "\n".join(story_lines)

        yield story


