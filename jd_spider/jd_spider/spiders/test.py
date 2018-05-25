import requests
import time
from lxml import etree
from fake_useragent import UserAgent
import json


class Test(object):

    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random
        }

    def parse_info(self, url):
        r = requests.get(url, headers=self.headers)
        html = etree.HTML(r.text)
        # 解析商品urls
        goods_info_html = html.xpath(r'//div[@id="plist"]/ul/li')
        items_dict = {}  # 用来存放item的字典，用来统一访问价格，和总体评论信息,减少服务器的压力
        i = 0
        for each_good in goods_info_html:
            # 解析每个商品的信息
            goods_id = each_good.xpath(r'./div[@class="gl-i-wrap j-sku-item"]/@data-sku')[0]
            goods_name = each_good.xpath(r'./div[@class="gl-i-wrap j-sku-item"]/div[contains(@class, "p-name")]/a/em/text()')
            goods_name = ''.join(goods_name).strip()
            i += 1
            # print(i)
            # print(goods_id)
            # print(goods_name)
            items = {
                'goods_id': goods_id,
                'goods_name': goods_name,
            }
            items_dict[goods_id] = items

        # 构造价格访问url
        skuids = 'J_' + ',J_'.join(items_dict.keys())
        price_url = 'http://p.3.cn/prices/mgets?skuIds=' + skuids
        print(price_url)

    def parse_price(self, url):
        r = requests.get(url, headers=self.headers)
        print(r.text)

    def test1(self):
        url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=3888216&_=1526990531042'
        r = requests.get(url, headers=self.headers)
        response = json.loads(r.text)
        print(r.text)
        print(type(r.text))
        print(response['CommentsCount'])


if __name__ == '__main__':
    # url = 'https://list.jd.com/list.html?cat=737,738,747'
    url = 'https://list.jd.com/list.html?cat=737,1276,742'
    # price_url
    price_url = 'http://p.3.cn/prices/mgets?type=1&area=1_72_4137_0&skuIds=J_3679941%2CJ_1102494%2CJ_5806368%2CJ_526169%2CJ_5110201%2CJ_2219600%2CJ_5677229%2CJ_1103405%2CJ_1066649%2CJ_2373165%2CJ_5570406%2CJ_3831100%2CJ_10988538238%2CJ_1346386%2CJ_1498217%2CJ_10943300891%2CJ_10809199779%2CJ_975788%2CJ_6105909%2CJ_3831340%2CJ_1362705%2CJ_2373177%2CJ_5286449%2CJ_2099985%2CJ_1102495%2CJ_4167068%2CJ_2384789%2CJ_5323665%2CJ_4761246%2CJ_4110914%2CJ_1894492%2CJ_17259167703%2CJ_4114350%2CJ_1076553%2CJ_1274471%2CJ_26872760853%2CJ_3554736%2CJ_2220375%2CJ_1283753%2CJ_2927840%2CJ_3831078%2CJ_1331772%2CJ_1293672%2CJ_10716417589%2CJ_216238%2CJ_2373187%2CJ_2372354%2CJ_14939666248%2CJ_1285571%2CJ_3244140%2CJ_1498224%2CJ_4182530%2CJ_5110235%2CJ_118340%2CJ_14939666242%2CJ_216237%2CJ_5285120%2CJ_280217%2CJ_12280966983%2CJ_1525513&pdbp=0&pdtk=&pdpin=&source=list_pc_front&_=' + str(int(time.time())*1000)
    crawl = Test()
    # crawl.parse_price(price_url)
    crawl.test1()
