from . import api
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from .. import redis_db, socketio
from secrets import token_urlsafe
from flask_socketio import disconnect, rooms
from ..exceptions import NotRoomError, NotConnectError
from config import STATICS_DEST

get_participants = socketio.server.manager.get_participants


class RoomAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sid', type=str, required=True, location=['json', 'form'])
        self.reqparse.add_argument('topic', type=str, required=False, location='form')
        self.reqparse.add_argument('desc', type=str, required=False, location='form')
        self.reqparse.add_argument('avatar', type=FileStorage, required=False, location='files')
        super().__init__()

    def post(self):
        self.reqparse.add_argument('name', type=str, required=True, location='form')
        args = self.reqparse.parse_args(strict=True)
        if not rooms(args['sid'], '/chat/rooms'):
            raise NotConnectError('无效的sid，房间创建失败')

        sid = args.pop('sid')
        room_id = token_urlsafe(16)  # 对应有16*4/3=22个字符
        while redis_db.exists(f'room_{room_id}'):
            room_id = token_urlsafe(16)

        avatar = args['avatar']
        if avatar is not None:
            avatar.save(STATICS_DEST+f'\\img\\room_{room_id}')  # 文件名不保留后缀，靠redis存mimetype
            args['avatar'] = avatar.mimetype

        room_info = {k: v for k, v in args.items() if v is not None}  # redis不允许None
        redis_db.hset(f'user_{sid}', 'room', room_id)  # with socketio.server.session(sid) as session
        redis_db.hmset(f'room_{room_id}', room_info)

        response = {'code': 0, 'msg': '', 'data': room_id}  # todo 应换成room_url
        return response, 201

    def delete(self):
        args = self.reqparse.parse_args(strict=True)
        sid = args['sid']
        room_id = redis_db.hget(f'user_{sid}', 'room')
        if room_id is None:
            raise NotRoomError('该房间不存在，删除失败')
        room_id = room_id.decode()

        for p in get_participants('/chat/rooms', room_id):
            disconnect(p, '/chat/rooms')
        # 引发on_disconnect，删掉p创建的房间，但实际上除房主外都不会建立房间，不会误删

        response = {'code': 0, 'msg': ""}
        return response, 200

    def put(self):
        self.reqparse.add_argument('name', type=str, required=True, location='form')
        args = self.reqparse.parse_args(strict=True)

        sid = args.pop('sid')
        room_id = redis_db.hget(f'user_{sid}', 'room')
        if room_id is None:
            raise NotRoomError()
        room_id = room_id.decode()

        avatar = args['avatar']
        if avatar is not None:
            avatar.save(STATICS_DEST+f'\\img\\room_{room_id}')
            args['avatar'] = avatar.mimetype

        room_info = {k: v for k, v in args.items() if v is not None}
        redis_db.hmset(f'room_{room_id}', room_info)

        response = {'code': 0, 'msg': "", 'data': room_id}  # todo 应换成room_url
        return response, 200


api.add_resource(RoomAPI, '/rooms', endpoint='rooms')
