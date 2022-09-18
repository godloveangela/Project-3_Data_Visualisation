import datetime
import decimal
import json
import random


# handle some object type which can not be serialized by json.dumps() function
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


# define request return json object structure
class R():
    def success(self, data=None, msg=None, code='0'):
        result = {
            'data': data,
            'msg': msg,
            'code': code
        }
        return json.dumps(result, cls=JsonEncoder)

    def error(self, data=None, msg=None, code='100'):
        result = {
            'data': data,
            'msg': msg,
            'code': code
        }
        return json.dumps(result)


# generate random color code
def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color