
import json
import redis
import pymongo


def main():

    # 指定Redis数据库信息
    rediscli = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    # 指定MongoDB数据库信息
    mongocli = pymongo.MongoClient(host='localhost', port=27017)

    # 创建数据库名
    db = mongocli['jingdong']
    # 创建表名
    sheet_goods = db['jd_goods']
    sheet_comment = db['jd_goods_comment']
    i = 1
    j = 1
    while True:
        # FIFO模式为 blpop，LIFO模式为 brpop，获取键值
        source, data = rediscli.blpop(["jd:items"])
        data = data.decode('utf-8')
        item = json.loads(data)
        if 'nickname' in item.keys():
            sheet_comment.insert(item)
            j += 1
        else:
            i += 1
            sheet_goods.insert(item)

        try:
            print("Processing: %(goods_id)s <%(goods_name)s>" % item)
        except KeyError:
            print("Processing: %(goods_id)s <%(content)s>" % item)
            # print(u"Error procesing: %r" % item)


if __name__ == '__main__':
    main()
