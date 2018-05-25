
import json

b1 = b'{"content": "\u8d28\u91cf\u5f88\u4e0d\u9519\u3002\u3002\u3002\u3002", "goods_id": "11821617", "user_client": "\u6765\u81ea\u4eac\u4e1cAndroid\u5ba2\u6237\u7aef", "reference_name": "\u8336\u7ecf", "create_time": "2017-11-11 16:22:51", "level_name": "\u91d1\u724c\u4f1a\u5458", "nickname": "J***6", "score": 5}'

str2 = b1.decode('utf8')
print(str2)
print(type(str2))

# str1 = json.loads(b2)
