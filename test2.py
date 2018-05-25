import requests
import json
from jsonpath import jsonpath
from lxml import etree
from urllib.parse import urlparse
from fake_useragent import UserAgent

'''
# 价格url
http://p.3.cn/prices/mgets?skuIds=J_19469079
# 总体评论url
http://club.jd.com/comment/productCommentSummaries.action?referenceIds=19469079
# 具体用户评论url
http://sclub.jd.com/comment/productPageComments.action?productId=19469079&score=0&sortType=5&page=0&pageSize=10
以上返回的都是json格式，解析相应的数据即可
'''
ua = UserAgent()
headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }


def send_request():
    url = 'https://list.jd.com/list.html?cat=1713,4855,4859'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0'
    }

    r = requests.get(url, headers=headers)

    html = etree.HTML(r.text)

    goods_urls = html.xpath(r'//div[@id="plist"]')
    for each in goods_urls:
        goods_url_list = each.xpath(r'.//@href')
        for each in goods_url_list:
            good_url = urlparse(each)
            if good_url.netloc:
                # 判断是商品详情url
                if good_url.hostname.split('.')[0] == 'item':
                    link = 'http:' + each
                    # 解析商品信息
                    parse_info(link)


def parse_info(response):
    html = etree.HTML(response.text)
    # 解析商品块
    goods_info_html = html.xpath(r'//div[@id="plist"]/ul/li')
    items_dict = {}  # 用来存放item的字典，用来统一访问价格，和总体评论信息,减少服务器的压力
    for each_good in goods_info_html:
        # 解析每个商品的信息
        goods_id = each_good.xpath(r'./div[@class="gl-i-wrap j-sku-item"]/@data-sku')[0]
        goods_name = each_good.xpath(r'./div[@class="gl-i-wrap j-sku-item"]/div[@class="p-name"]/a/em/text()')[0].strip()
        items = {
            'goods_id': goods_id,
            'goods_name': goods_name,
        }
        items_dict[goods_id] = items

    # 构造价格访问url
    skuids = 'J_' + ',J_'.join(items_dict.keys())
    price_url = 'http://p.3.cn/prices/mgets?skuIds=' + skuids
    parse_price(price_url, items_dict)


def parse_price(url, items_dic):
    response = requests.get(url, headers=headers)
    json_obj = json.loads(response.text)
    for each in json_obj:
        goods_id = each['id'].split('_')[1]
        items_dic[goods_id]['goods_price'] = each['p']

    # 构建评论url
    referenceids = ','.join(items_dic.keys())
    comment_url = 'http://club.jd.com/comment/productCommentSummaries.action?referenceIds=' + referenceids
    # 解析总体评论信息
    parse_comment_summerize(comment_url, items_dic)


def parse_comment_summerize(url, items_dict):
    response = requests.get(url, headers=headers)
    jsonobj = json.loads(response.text)
    print(jsonobj)
    for each in jsonobj['CommentsCount']:
        goods_id = str(each['ProductId'])
        items_dict[goods_id]['GoodRate'] = each['GoodRate']
        items_dict[goods_id]['CommentCount'] = each['CommentCountStr']
        items_dict[goods_id]['ShowCount'] = each['ShowCountStr']
        items_dict[goods_id]['PoorCount'] = each['PoorCountStr']
        items_dict[goods_id]['AverageScore'] = each['AverageScore']
        items_dict[goods_id]['DefaultGoodCount'] = each['DefaultGoodCountStr']
        items_dict[goods_id]['AfterCount'] = each['AfterCountStr']
        items_dict[goods_id]['GoodCount'] = each['GoodCountStr']
    print(items_dict)


def send_request2(url):

    r = requests.get(url, headers=headers)

    # 解析相关信息
    # print(r.text)
    # parse_info(r)
    parse_comment_info(r)


def parse_comment_info(response):
    jsonobj = json.loads(response.text)
    items = jsonpath(jsonobj, '$.comments')[0]
    print(items)


if __name__ == '__main__':
    # url = 'http://item.jd.com/19469079.html'
    # url = 'https://list.jd.com/list.html?cat=1713,4855,4859'
    url = 'http://sclub.jd.com/comment/productPageComments.action?productId=19469079&score=0&sortType=5&page=0&pageSize=10'
    send_request2(url)

