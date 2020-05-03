from . import api
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from .. import redis_db, socketio
from secrets import token_urlsafe
from flask_socketio import disconnect, rooms
from ..exceptions import NotRoomError, NotConnectError, UpTypeError
from config import STATICS_DEST, MSG_PER_PAGE, ALLOWED_IMG_EXT, DEFAULT_AVATAR
from json import loads
from flask import url_for
from os import remove
from time import time

get_participants = socketio.server.manager.get_participants


def store_avatar(img, key):
    m_type = img.mimetype.split('/')
    if m_type[0] != 'image' or m_type[1] not in ALLOWED_IMG_EXT:
        raise UpTypeError('检查图片后缀是否存在且合法')
    # 图片靠nginx代理，redis保存文件名仅供更新删除

    filename = redis_db.hget(key, 'avatar')
    if filename and filename != DEFAULT_AVATAR:
        remove(STATICS_DEST + filename)

    filename = f'{token_urlsafe(3)}{time()}.{m_type[1]}'
    img.save(STATICS_DEST + filename)  # 头像须公开但sid敏感，不能含sid
    return filename


def store_info(args, room_id):
    avatar = args['avatar']
    room_key = f'room_{room_id}'

    if avatar is not None:
        args['avatar'] = store_avatar(avatar, room_key)

    room_info = {k: v for k, v in args.items() if v is not None}  # redis不允许None
    redis_db.hmset(room_key, room_info)


class RoomAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('topic', type=str, required=False, location='form')
        self.reqparse.add_argument('desc', type=str, required=False, location='form')
        self.reqparse.add_argument('avatar', type=FileStorage, required=False, location='files')
        super().__init__()

    def post(self):
        self.reqparse.add_argument('sid', type=str, required=True, location='form')
        self.reqparse.add_argument('name', type=str, required=True, location='form')
        args = self.reqparse.parse_args(strict=True)
        if not rooms(args['sid'], '/chat'):
            raise NotConnectError('无效的sid，房间创建失败')

        sid = args.pop('sid')
        room_id = token_urlsafe(16)  # 对应有16*4/3=22个字符
        while redis_db.exists(f'room_{room_id}'):
            room_id = token_urlsafe(16)

        store_info(args, room_id)
        redis_db.hset(f'user_{sid}', 'room', room_id)

        response = {'code': 0, 'msg': '', 'data': room_id}
        return response, 201

    def delete(self):
        self.reqparse.add_argument('sid', type=str, required=True, location='args')
        args = self.reqparse.parse_args(strict=True)
        sid = args['sid']
        room_id = redis_db.hget(f'user_{sid}', 'room')
        if room_id is None:
            raise NotRoomError('该房间不存在，或无权删除')

        for p in get_participants('/chat', room_id):
            disconnect(p, '/chat')
        # 引发on_disconnect，删掉p创建的房间，但实际上除房主外都不会建立房间，不会误删

        response = {'code': 0, 'msg': ""}
        return response, 200

    def put(self):
        self.reqparse.add_argument('sid', type=str, required=True, location='form')
        self.reqparse.add_argument('name', type=str, required=True, location='form')
        args = self.reqparse.parse_args(strict=True)

        sid = args.pop('sid')
        room_id = redis_db.hget(f'user_{sid}', 'room')
        if room_id is None:
            raise NotRoomError('该房间不存在，或无权修改')

        store_info(args, room_id)

        response = {'code': 0, 'msg': "", 'data': room_id}
        return response, 200

    def get(self):
        self.reqparse.add_argument('room', type=str, required=True, location='args')
        args = self.reqparse.parse_args(strict=True)
        room_id = args["room"]

        room_info = redis_db.hgetall(f'room_{room_id}')
        filename = room_info.get('avatar', '') or DEFAULT_AVATAR
        room_info['avatar'] = url_for('main.get_avatar', filename=filename)

        response = {'code': 0, 'msg': "", 'data': room_info}
        return response, 200


class MsgHistoryAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('room', type=str, required=True, location='args')
        self.reqparse.add_argument('mid', type=int, required=True, location='args')
        self.reqparse.add_argument('ps', type=int, required=False, default=3, location='args')
        super().__init__()

    def get(self):
        args = self.reqparse.parse_args(strict=True)
        room_id, mid, ps = args['room'], args['mid'], args['ps']
        msg_key = f'msg_{room_id}'
        m_len = redis_db.llen(msg_key)

        if mid == -1:  # 第一次请求得知当前时间点往前的历史消息数，不返回消息
            data = {'left': m_len, 'list': []}  # left: 剩余未取数量
        else:
            ps = 1 if ps < 1 else (MSG_PER_PAGE if ps > MSG_PER_PAGE else ps)  # 0<ps<MSG_PER_PAGE
            mid = m_len-1 if mid > m_len else 0 if mid <= 0 else mid  # -1<mid<m_len, 与begin相对，充当end
            begin = mid-ps+1 if mid >= ps else 0  # -1<begin<=end

            msg_list = redis_db.lrange(msg_key, begin, mid)
            msg_list = list(map(lambda x: loads(x), msg_list))
            data = {'left': begin, 'list': msg_list[::-1]}  # left=begin=0说明获取完毕

        response = {'code': 0, 'msg': "", 'data': data}
        return response, 200


class UserAvatarAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sid', type=str, required=True, location=['args', 'form'])
        super().__init__()

    def get(self):
        args = self.reqparse.parse_args(strict=True)
        user_key = f"user_{args['sid']}"

        filename = redis_db.hget(user_key, 'avatar') or DEFAULT_AVATAR
        response = {'code': 0, 'msg': "", 'data': url_for('main.get_avatar', filename=filename)}
        return response, 200

    def put(self):
        self.reqparse.add_argument('avatar', type=FileStorage, required=True, location='files')
        args = self.reqparse.parse_args(strict=True)

        user_key = f"user_{args['sid']}"
        filename = store_avatar(args['avatar'], user_key)
        redis_db.hset(user_key, 'avatar', filename)

        response = {'code': 0, 'msg': ""}
        return response, 200


api.add_resource(RoomAPI, '/rooms', endpoint='rooms')
api.add_resource(MsgHistoryAPI, '/messages', endpoint='messages')
api.add_resource(UserAvatarAPI, '/users/avatar', endpoint='avatar')
