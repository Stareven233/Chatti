import json

json_config = {'ensure_ascii': False, 'indent': None, 'separators': (',', ':')}


class ChatException(Exception):
    def __init__(self, code, message, sid):
        self.code = code
        self.message = message
        self.sid = sid

    def __str__(self):
        response = {'code': self.code, 'msg': self.message}
        return json.dumps(response, **json_config)


class UserAlreadyExistsError(ChatException):
    pass


class IncorrectPasswordError(ChatException):
    pass
