from . import api
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from .. import redis_db, socketio
from secrets import token_urlsafe
from flask_socketio import disconnect, rooms
from ..exceptions import NotRoomError, NotConnectError
from flask import current_app, g, send_from_directory, url_for

get_participants = socketio.server.manager.get_participants


class RoomAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sid', type=str, required=True, location=['json', 'form'])
        self.reqparse.add_argument('topic', type=str, required=False, location='form')
        self.reqparse.add_argument('desc', type=str, required=False, location='form')
        self.reqparse.add_argument('avatar', type=FileStorage, required=False, location='files')  # todo 头像改成必须
        super().__init__()

    def post(self):
        self.reqparse.add_argument('name', type=str, required=True, location='form')
        args = self.reqparse.parse_args(strict=True)
        if not rooms(args['sid'], '/chat/rooms'):
            raise NotConnectError('无效的sid，房间创建失败')

        if args['avatar'] is not None:
            args['avatar'] = args['avatar'].read()
        sid = args.pop('sid')
        room_info = {k: v for k, v in args.items() if v is not None}
        room_id = token_urlsafe(16)  # 对应有16*4/3=22个字符
        while redis_db.exists(f'room_{room_id}'):
            room_id = token_urlsafe(16)

        redis_db.hset(f'user_{sid}', 'room', room_id)  # with socketio.server.session(sid) as session
        redis_db.hmset(f'room_{room_id}', room_info)
        response = {'code': 0, 'msg': "", 'data': room_id}  # todo 应换成room_url
        return response, 201

    def delete(self):
        args = self.reqparse.parse_args(strict=True)
        sid = args['sid']
        room_id = redis_db.hget(f'user_{sid}', 'room').decode()
        if room_id is None:
            raise NotRoomError('该房间不存在，不可删除')
        for p in get_participants('/chat/rooms', room_id):
            disconnect(p, '/chat/rooms')
        # 引发on_disconnect，删掉p创建的房间，但实际上除房主外都不会建立房间，不会误删
        response = {'code': 0, 'msg': ""}
        return response, 200

    def put(self):
        self.reqparse.add_argument('name', type=str, required=True, location='form')
        args = self.reqparse.parse_args(strict=True)

        sid = args.pop('sid')
        room_id = redis_db.hget(f'user_{sid}', 'room').decode()
        if room_id is None:
            raise NotRoomError()
        room_info = {k: v for k, v in args.items() if v is not None}
        redis_db.hmset(f'room_{room_id}', room_info)

        response = {'code': 0, 'msg': ""}  # todo 应换成room_url
        return response, 200


api.add_resource(RoomAPI, '/rooms', endpoint='rooms')
