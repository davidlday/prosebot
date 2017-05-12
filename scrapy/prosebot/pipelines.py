# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
from scrapy.exceptions import DropItem
import requests


class ProsebotPipeline(object):
    def process_item(self, item, spider):
        return item


class BookwormRestApiPipeline(object):
    def process_item(self, item, spider):
        if item['text'] == '':
            raise DropItem("Story %s at %s has no content." %(item['title'], item['url']))
        else:
            text = item.get('text')

            # Invoke the bookworm analysis service
            url         = settings.get('BOOKWORM_REST_URI')
            prose       = { 'prose': text }
            ret         = requests.post(url,json=prose)
            bookworm    = ret.json()
            item.update(bookworm)

        return item
