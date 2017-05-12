# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Story(scrapy.Item):
    # Basics - captured in spiders
    url = scrapy.Field()
    magazine = scrapy.Field()
    pub_month = scrapy.Field()
    pub_year = scrapy.Field()
    pub_date = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    genre = scrapy.Field()
    original_tags = scrapy.Field()
    text = scrapy.Field()

#   bookworm = scrapy.Field()

#   Metadata
    bytes = scrapy.Field()

#   Syllables, Words, Sentences, Paragraphs
    syllable_count = scrapy.Field()
    word_count = scrapy.Field()
    unique_words = scrapy.Field()
    unique_word_count = scrapy.Field()
    complex_word_count = scrapy.Field()
    avg_syllables_per_word = scrapy.Field()
    sentence_count = scrapy.Field()
    avg_words_per_sentence = scrapy.Field()
    word_frequency = scrapy.Field()
    paragraph_count = scrapy.Field()
    long_word_count = scrapy.Field()

#   Readability Scores
    flesch_reading_ease = scrapy.Field()
    flesch_kincaid_grade_level = scrapy.Field()
    gunning_fog_index = scrapy.Field()
    coleman_liau_index = scrapy.Field()
    smog_index = scrapy.Field()
    automated_readability_index = scrapy.Field()
    lix = scrapy.Field()
    rix = scrapy.Field()

#   Point of View
    pov_indicators = scrapy.Field()
    pov = scrapy.Field()
    pov_indicator_frequency = scrapy.Field()

#   Dialogue vs. Narrative
    dialogue_unique_words = scrapy.Field()
    dialogue_word_count = scrapy.Field()
    dialogue_syllable_count = scrapy.Field()
    dialogue_unique_word_count = scrapy.Field()
    dialogue_word_frequency = scrapy.Field()
    narrative_word_count = scrapy.Field()
    narrative_unique_word_count = scrapy.Field()
    narrative_syllable_count = scrapy.Field()
    narrative_word_frequency = scrapy.Field()
    dialogue_word_percentage = scrapy.Field()
    dialogue_syllable_percentage = scrapy.Field()
