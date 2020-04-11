from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import BaseResponse
from json import dumps

json_config = {'ensure_ascii': False, 'indent': None, 'separators': (',', ':')}


class MyApiError(HTTPException):
    e_code = 0

    def __init__(self, description=None):
        super().__init__(description)
        resp = BaseResponse(response=self.to_json(), status=self.code, mimetype='application/json')
        self.response = resp

    def to_json(self):
        response = {'code': self.e_code, 'msg': self.description}
        return dumps(response, **json_config)


class NotRoomError(MyApiError):
    code = 404
    description = '不存在该房间'
    e_code = 1101


class NotConnectError(MyApiError):
    code = 400
    description = '连接未建立'
    e_code = 1102
