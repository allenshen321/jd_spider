# jd_spider
scrapy， 商品和评论信息

##### 1、京东分类首页，提取所有的分类
https://www.jd.com/allSort.aspx

**xpath规则**

url_list = html.xpath(r'//div[@class="list"]//a/@href')

**筛选url中是商品列表的**

    r = requests.get(url, headers=headers)
    html = etree.HTML(r.text)
    url_list = html.xpath(r'//@href')
    # 筛选商品列表url
    for url in url_list:
        url2 = urlparse(url)
        if url2.netloc == 'list.jd.com':
            full_url = 'https:' + url

##### 2、提取分类下的商品url

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
        
 此处，将信息放到一个字典中，是为了提取当前页中所有的商品，以便于后续步骤用一个请求将当前页面所有的商品的价格和评价信息一起请求，这样可以大大减少请求的次数。
 
    # 构造价格访问url 
    skuids = 'J_' + ',J_'.join(items_dict.keys())
    price_url = 'http://p.3.cn/prices/mgets?skuIds=' + skuids
 
 ##### 3、提取价格信息放入上一步构建的字典
 
 价格信息返回的是json格式的数据。
 
    json_obj = json.loads(response.text)
    for each in json_obj:
        goods_id = each['id'].split('_')[1]
        items_dic[goods_id]['goods_price'] = each['p']
        
 ##### 4、 构造总体评论url
 
     # 构建评论url
    referenceids = ','.join(items_dict.keys())
    comment_url = 'http://club.jd.com/comment/productCommentSummaries.action?referenceIds=' + referenceids
 
 ##### 5、 解析评论综述
 
    jsonobj = json.loads(response.text)
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
    







