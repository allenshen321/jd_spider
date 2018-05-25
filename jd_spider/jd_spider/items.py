# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdSpiderItem(scrapy.Item):
    """商品详情"""
    # define the fields for your item here like:
    # name = scrapy.Field()
    goods_url = scrapy.Field()
    goods_id = scrapy.Field()
    goods_name = scrapy.Field()
    goods_price = scrapy.Field()
    good_rate = scrapy.Field()
    comment_count = scrapy.Field()
    show_count = scrapy.Field()
    poor_count = scrapy.Field()
    average_score = scrapy.Field()
    default_good_count = scrapy.Field()
    after_count = scrapy.Field()
    good_count = scrapy.Field()


class JdSpiderCommentItem(scrapy.Item):
    """评论"""
    goods_id = scrapy.Field()
    nickname = scrapy.Field()
    level_name = scrapy.Field()
    user_client = scrapy.Field()
    score = scrapy.Field()
    reference_name = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field()
