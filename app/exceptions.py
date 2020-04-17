from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import BaseResponse
from . import compact_dumps


class MyApiError(HTTPException):
    e_code = 0

    def __init__(self, description=None):
        super().__init__(description)
        resp = BaseResponse(response=self.to_json(), status=self.code, mimetype='application/json')
        self.response = resp

    def to_json(self):
        response = {'code': self.e_code, 'msg': self.description}
        return compact_dumps(response)


class NotRoomError(MyApiError):
    code = 404
    description = '不存在该房间，或room_id错误'
    e_code = 1101


class NotConnectError(MyApiError):
    code = 400
    description = '连接未建立，或sid错误'
    e_code = 1102


class UpTypeError(MyApiError):
    code = 415
    description = '未表明文件类型或类型非法'
    e_code = 1103
