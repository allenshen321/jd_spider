
import requests
import lxml
from lxml import etree
from urllib.parse import urlparse


url = 'https://www.jd.com/allSort.aspx'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0'
}

r = requests.get(url, headers=headers)

html = etree.HTML(r.text)
url_list = html.xpath(r'//@href')
# 筛选商品列表url
for url in url_list:
    url2 = urlparse(url)
    if url2.netloc == 'list.jd.com':
        full_url = 'https:' + url
        print(full_url)

