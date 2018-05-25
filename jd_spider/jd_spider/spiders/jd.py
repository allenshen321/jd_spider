# -*- coding: utf-8 -*-
import scrapy
import json
import jsonpath
import time

from jd_spider.items import JdSpiderItem, JdSpiderCommentItem
from urllib.parse import urlparse
from lxml import etree
from scrapy_redis.spiders import RedisSpider


class JdSpider(RedisSpider):
    name = 'jd'
    # start_urls = ['https://www.jd.com/allSort.aspx']
    redis_key = 'JdSpider:start_urls'

    def parse(self, response):
        html = etree.HTML(response.text)
        url_list = html.xpath(r'//@href')
        # 筛选商品列表url
        for url in url_list:
            url2 = urlparse(url)
            if url2.netloc == 'list.jd.com':
                full_url = 'https:' + url
                yield scrapy.Request(full_url, callback=self.parse_goods_urls)

    def parse_goods_urls(self, response):
        # 解析商品urls
        goods_info_html = response.xpath(r'//div[@id="plist"]/ul/li')
        for each_good in goods_info_html:
            # 解析每个商品的信息
            goods_id = each_good.xpath(r'./div[@class="gl-i-wrap j-sku-item"]/@data-sku').extract_first()
            goods_name = each_good.xpath(r'./div[@class="gl-i-wrap j-sku-item"]/div[contains(@class, '
                                         r'"p-name")]/a/em/text()').extract()
            goods_url = each_good.xpath(
                r'./div[@class="gl-i-wrap j-sku-item"]/div[contains(@class, "p-name")]/a/@href').extract_first()
            goods_url = 'https:' + goods_url
            goods_name = ''.join(goods_name).strip()
            # 构建商品信息item
            items = JdSpiderItem(goods_id=goods_id, goods_name=goods_name, goods_url=goods_url)

            if goods_name:
                # 构造价格访问url
                skuids = 'J_' + goods_id
                price_url = 'http://p.3.cn/prices/mgets?type=1&area=1_72_4137_0&skuIds=' + skuids + '&pdpin=&pin=null&pdbp=0&pdtk=&pdpin=&source=list_pc_front&_=' + str(
                    int(time.time() * 1000))
                # 请求价格信息
                # print('请求价格url')
                yield scrapy.Request(price_url, callback=self.parse_price, meta={'items_dict': items})

        # 判断下一页url
        try:
            is_next = response.xpath(r'//span[@class="p-num"]/a[@class="pn-next"]/@href').extract()[0]
            is_next_page = 'https://list.jd.com' + is_next
        except Exception as e:
            max_page = response.xpath(r'//span[@class="p-num"]/a[last()]/text()').extract()
            if not max_page:
                max_page = str(1)
            category = urlparse(response.url).query.split('&')[0]
            print('----------%s共有: %s页----------' % (category, max_page))
            # self.log('----------%s共有: %s页----------' % (category, max_page))
            is_next_page = False
        # 判断是否继续下一页请求
        if is_next_page:
            yield scrapy.Request(is_next_page, callback=self.parse_goods_urls)

    def parse_price(self, response):
        items_dict = response.meta['items_dict']
        json_obj = json.loads(response.text)
        # 有时候返回时错误的信息
        # 正常的返回应该是：[{'p': '1529.00', 'id': 'J_14577083377', 'm': '1899.00', 'op': '1529.00'}]
        # 错误的返回时： {'error': 'pdos_captcha'}
        # 返回结果是列表形式
        is_have_price = True  # 用来判断返回价格信息是否正确,如果是True则正确，如果是False则重新发送请求
        try:
            items_dict['goods_price'] = json_obj[0]['p']
        except Exception as e:
            # 重新发送请求
            yield scrapy.Request(response.url, callback=self.parse_price, meta=response.meta, dont_filter=True)
            is_have_price = False

        if is_have_price:
            # 构建评论url
            referenceids = items_dict['goods_id']
            comment_url = 'http://club.jd.com/comment/productCommentSummaries.action?referenceIds=' + referenceids + '&_=' + str(
                int(time.time() * 1000))
            # 请求商品评价信息
            # print('请求商品url')
            yield scrapy.Request(comment_url, callback=self.parse_comment_info, meta={'items_dict': items_dict})

    def parse_comment_info(self, response):
        # 接受传递的数据
        items_dict = response.meta['items_dict']
        # print(items_dict)
        # 解析总体评价信息
        jsonobj = json.loads(response.text)
        # print(jsonobj)
        for each in jsonobj['CommentsCount']:
            items_dict['good_rate'] = each['GoodRate']
            items_dict['comment_count'] = each['CommentCountStr']
            items_dict['show_count'] = each['ShowCountStr']
            items_dict['poor_count'] = each['PoorCountStr']
            items_dict['average_score'] = each['AverageScore']
            items_dict['default_good_count'] = each['DefaultGoodCountStr']
            items_dict['after_count'] = each['AfterCountStr']
            items_dict['good_count'] = each['GoodCountStr']

            # 提交数据
            yield items_dict

            # 构造具体商品的评价url
            max_comment_num = items_dict['show_count'].replace('+', '')
            if '万' in max_comment_num:
                max_comment_num = max_comment_num.replace('万', '')
                max_comment_num = float(max_comment_num) * 10000
            # 判断有多少页
            if int(max_comment_num) > 0:
                max_comment_page_num = int(max_comment_num) // 10 + 1
            else:
                max_comment_page_num = 0
            for page in range(max_comment_page_num):
                product_comment_url = 'http://sclub.jd.com/comment/productPageComments.action?' \
                                      'productId=' + items_dict["goods_id"] + '&score=0&sortType=5&' \
                                                                              'page=' + str(page) + '&pageSize=10'
                yield scrapy.Request(
                    product_comment_url,
                    meta={'goods_id': items_dict['goods_id']},
                    callback=self.parse_product_comment
                )

    def parse_product_comment(self, response):
        try:
            jsonobj = json.loads(response.text)
        except:
            yield scrapy.Request(response.url, callback=self.parse_product_comment)
            jsonobj = None
        if jsonobj:
            # 每页10个item
            items = jsonpath.jsonpath(jsonobj, '$.comments')[0]
            goods_id = response.meta.get('goods_id', '')
            for each_item in items:
                nickname = each_item.get('nickname', '')
                level_name = each_item.get('userLevelName', '')
                user_client = each_item.get('userClientShow', '')
                score = each_item.get('score', '')
                reference_name = each_item.get('referenceName', '')
                content = each_item.get('content', '')
                create_time = each_item.get('creationTime', '')
                # 构建评论信息item
                comment_item = JdSpiderCommentItem(
                    goods_id=goods_id,
                    nickname=nickname,
                    level_name=level_name,
                    user_client=user_client,
                    score=score,
                    reference_name=reference_name,
                    content=content,
                    create_time=create_time
                )
                yield comment_item
