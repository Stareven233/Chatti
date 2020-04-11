from .. import socketio, redis_db
from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
import json
from .exceptions import UserAlreadyExistsError

json_config = {'ensure_ascii': False, 'indent': None, 'separators': (',', ':')}
get_participants = socketio.server.manager.get_participants


@socketio.on('connect', namespace='/chat/rooms')
def on_connect():
    print('连接上了', request.sid)


@socketio.on('disconnect', namespace='/chat/rooms')
def on_disconnect():
    room_destroy()
    print('关闭了连接', request.sid)


@socketio.on('build', namespace='/chat/rooms')
def room_build(data):
    avatar = data.pop('avatar', '')
    data = json.dumps(data, **json_config)
    redis_db.hset('room_avatars', request.sid, avatar)  # 以base64保存房间头像
    redis_db.rpush(f'room_{request.sid}', data)         # 推入房间信息

    room_url = f'/chat/{request.sid}'
    response = json.dumps({'code': 0, 'msg': "", 'data': room_url}, **json_config)
    emit('build', response, room=request.sid)


@socketio.on('destroy', namespace='/chat/rooms')
def room_destroy():
    sid = request.sid  # todo 待测试
    if not sid:
        return
    for p in get_participants('/chat/rooms', sid):
        if p != request.sid:
            disconnect(p)                       # 断开其他成员
    redis_db.hdel('room_avatars', sid)          # 删除该房间头像
    redis_db.delete(f'room_{sid}')              # 删除该房间


@socketio.on('set_room', namespace='/chat/rooms')
def room_set(data):  # todo 还未测试
    avatar = data.pop('avatar', '')
    data = json.dumps(data, **json_config)
    response = {'code': 0, 'msg': '', 'data': ''}

    if not redis_db.exists(f'room_{request.sid}'):
        pass
    if avatar:
        redis_db.hset('room_avatars', request.sid, avatar)      # 以base64保存房间头像
    if data:
        redis_db.lset(f'room_{request.sid}', 0, data)           # 推入房间信息

    response = json.dumps(response, **json_config)
    emit('response', response, room=request.sid)


@socketio.on('join', namespace='/chat/rooms')
def on_join(data):
    join_room(data['room'])  # todo 考虑到client过来的可能是json
    # name = redis_db.lindex(f'room_{room}', 0)
    # print(name.decode())
    emit('response', data['username'] + '加入了房间', broadcast=True, room=data['room'])


@socketio.on('leave', namespace='/chat/rooms')
def on_leave(data):
    leave_room(data['room'])  # todo 考虑到client过来的可能是json
    emit('response', data['username'] + '离开了房间', broadcast=True, room=data['room'])


@socketio.on('chat', namespace='/chat/rooms')
def on_chatting(data):
    emit('chat', data, broadcast=True, room=data['room'])  # , include_self=False


@socketio.on('test', namespace='/chat/rooms')
def on_test():
    raise UserAlreadyExistsError(1000, '用户已存在', request.sid)
    # print(rooms(data['sid']))
    # members = list(get_participants('/chat/rooms', data['sid']))
    # info = json.dumps(members, **json_config)
    # print(len(members), info)
