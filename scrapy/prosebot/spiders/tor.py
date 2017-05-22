import scrapy
import calendar
import re
import dateutil.parser
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor

# Tor.com seems to be using CloudFlare and the Bad Behavior WP plugin.
# * http://marketersbraintrust.com/bad-behavior-cloudflare/
# Attempted rotating the user agent, but no luck.
# * http://tangww.com/2013/06/UsingRandomAgent/
# * https://stackoverflow.com/questions/8372703/how-can-i-use-different-pipelines-for-different-spiders-in-a-single-scrapy-proje
class TorSpider(CrawlSpider):
    name            = 'tor'
    magazine_name   = 'Tor.com'
    allowed_domains = ['tor.com']
    page_url        = 'http://www.tor.com/category/all-fiction/original-fiction/page/%s/'
    page            = 1
    start_urls      = [page_url % page]
    content_xpath   = '//div[@id="infinite-scroll-wrapper"]'
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=([
                    '/category/all-fiction/original-fiction/',
                    '/category/all-fiction/original-fiction/page/\d+/'
                ]),
                restrict_xpaths=(content_xpath)
            ),
            process_links='inject_next_page'
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=([
                    '/\d{4}/\d{2}/\d{2}/.+'
                ]),
                deny=([
                    '/category/all-fiction/original-fiction/',
                    '/category/all-fiction/original-fiction/page/\d+/',
                    '/features/series.*',
                    '/galleries.*',
                    '/community.*',
                    '/imprint',
                    '/page/.*',
                    '/blogs/.*',
                    '/tags/.*',
                    '/bloggers',
                    '/.+\#filter',
                    '/page/subscribe-to-torcom-rss-feeds',
                    '/stories/prose\?order=title',
                    '/stories/prose\?order=author',
                    '/bios/authors/.+',
                ]),
                restrict_xpaths=(content_xpath)
            ),
            callback='parse_story'
        ),
    )


    # Inject the next page url in avoidance of Infinite Scroll
    def inject_next_page(self, links):
        self.page += 1
        next_page = Link(self.page_url % self.page, "Page %s" % self.page)
        links.append(next_page)
        return links


    def parse_story(self, response):
        base_xpath      = '//article[contains(@class,"category-original-fiction")]'
        story_post      = response.xpath(base_xpath)
        story_lines     = []

        story           = Story()
        story['magazine'] = self.magazine_name
        story['genre']  = ['science fiction','fantasy','horror']
        story['url']    = response.url
        story['original_tags'] = response.xpath('//a[contains(@rel, "category")]/text()').extract()
        story['title'] = response.xpath('//meta[@property="og:title"]/@content').extract()
        story['author'] = response.xpath('//a[contains(@rel, "author")]/text()').extract()

        # Extract Published Month / Year
        published_datetime = dateutil.parser.parse(response.xpath('//meta[@property="article:published_time"]/@content').extract()[0])
        story['pub_year'] = str(published_datetime.year)
        pub_month_no = "%02d" % published_datetime.month
        pub_day = "%02d" % published_datetime.day
        story['pub_month'] = calendar.month_name[published_datetime.month].lower()
        story['pub_date'] = story['pub_year'] + '-' + pub_month_no + '-' + pub_day

        # Extract the body of the story
        story_lines = [p.strip() for p in story_post.xpath('//div[@class="entry-content"]/p[not(@class)]/text()').extract()]
        story['text']   = "\n".join(story_lines)

        yield story
