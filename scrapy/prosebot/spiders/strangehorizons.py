import scrapy
import re
import calendar
from prosebot.items import Story
from scrapy.spiders import CrawlSpider, Rule
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor


class StrangeHorizonsSpider(CrawlSpider):
    name            = "strangehorizons"
    allowed_domains = ["strangehorizons.com"]
    page_url        = "http://strangehorizons.com/fiction/page/%s/"
    page            = 1
    start_urls      = [page_url % page]
    rules           = (
        # Fiction index pages.
        Rule(LinkExtractor(
                allow=(
                    ['/fiction/', '/fiction/page/\d{1,}/']
                ),
                deny=('/fiction/.+/'),
                restrict_xpaths=('//div[contains(@class, "archive-right-sidebar")]')
            ),
            process_links='inject_next_page'
        ),
        # Fiction stories.
        Rule(LinkExtractor(
                allow=(
                    '/fiction/.+/',
                ),
                deny=(
                    '/fiction/page/\d{1,}/',
                    '/fiction/.+/#print',
                    '/fiction/.+/?share=.+',
                    '/fiction/reprint/',
                    '/\d{4}/\d{8}/.*podcast-f.shtml',
                    '/art.shtml',
                    '/articles.shtml',
                    '/columns.shtml',
                    '/fiction.shtml',
                    '/poetry.shtml',
                    '/reviews',
                    '/Archive.html',
                    '/AboutUs.shtml',
                    '/StaffList.shtml',
                    '/Guidelines.shtml',
                    '/WhoWeAre.shtml#contact',
                    '/Awards.shtml',
                    '/Jobs.shtml',
                    '/fund_drives/.*',
                    '//ubbthreads/ubbthreads.php',
                    '/blog',

                )
            ), callback='parse_story'
        ),
    )


    # Inject the next page url in avoidance of Infinite Scroll
    def inject_next_page(self, links):
        self.page += 1
        next_page = Link(self.page_url % self.page, "Page %s" % self.page)
        links.append(next_page)
        return links


    def parse_story(self, response):
        base_xpath      = '//div[contains(@class,"post-container")]/div[@class="post"]'
        story_post      = response.xpath(base_xpath)
        text            = ''

        story           = Story()
        story['magazine'] = "Strange Horizons"
        story['genre']  = ['speculative fiction']
        story['original_tags'] = story_post.xpath('.//a[contains(@rel, "category tag")]/text()').extract()
        story['url']    = response.url
        story['title']  = story_post.xpath('./div[@class="title"]/a/text()').extract()
        story['author']  = story_post.xpath('./div[@class="byline"]/div[@class="author"]/a/text()').extract()

        # Original date logic. Failed once due to inconsistent formatting.
        # Easy fix would be to check date string for a comma, and parse appropriately
        # See http://www.strangehorizons.com/2009/20090921/dark-f.shtml for failed story.
        month_name_no = dict((v.lower(),"%02d" % k) for k,v in enumerate(calendar.month_name))
        [pub_day, pub_month_name, pub_year] = story_post.xpath('./div[@class="byline"]/div[@class="date"]/a/text()').extract()[0].split()
        story['pub_month'] = pub_month_name.strip().lower()
        story['pub_year'] = pub_year.strip()
        pub_day = "%02d" % int(pub_day)
        story['pub_date'] = story['pub_year'] + '-' + month_name_no[story['pub_month']] + '-' + pub_day

        # Extract the body of the story
        story_lines = [p.strip() for p in story_post.xpath('.//div[contains(@class,"content")]/p[not(@class)]//text()').extract()]
        story['text']   = "\n".join(story_lines)

        yield story
