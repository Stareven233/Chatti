from .. import socketio, redis_db, compact_dumps
from flask_socketio import emit, join_room, leave_room, disconnect, rooms
from flask import request
from config import STATICS_DEST
from os import remove


get_participants = socketio.server.manager.get_participants
r_members = socketio.server.manager.rooms
# r_members[namespace][room_id]: 获取房间成员，可用于计算长度，字典类型，不可在迭代中删除键


@socketio.on('connect', namespace='/chat')
def on_connect():
    print('连接上了', request.sid)


@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    room_id = redis_db.hget(f'user_{request.sid}', 'room')
    if room_id is None:
        return
    room_key = f'room_{room_id}'

    if room_id in rooms():  # 最后1人断开时socket会删去记录，此if为False
        for p in get_participants('/chat', room_id):
            disconnect(p)  # 将该用户创建房间中其他人踢出

    avatar = redis_db.hget(room_key, 'avatar')
    if avatar:
        remove(STATICS_DEST + f'\\img\\{avatar}')
    redis_db.delete(f'user_{request.sid}', room_key, f'msg_{room_id}')
    print('关闭了连接', request.sid)


@socketio.on('join', namespace='/chat')
def on_join(data):
    room_id = data.pop('room', '')
    if not redis_db.exists(f'room_{room_id}'):
        return
    join_room(room_id)  # 房主自己也得join
    print('有人加入了？')
    emit('online_delta', 1, broadcast=True, room=room_id)
    emit('response', data['uname'] + '加入了房间', broadcast=True, room=room_id)


@socketio.on('leave', namespace='/chat')
def on_leave(data):
    room_id = data.pop('room', '')
    if room_id not in rooms():
        return
    leave_room(room_id)
    print('有人离开了？')
    emit('online_delta', -1, broadcast=True, room=room_id)
    emit('response', data['uname'] + '离开了房间', broadcast=True, room=room_id)


@socketio.on('chat', namespace='/chat')
def on_chatting(data):
    room_id = data.pop('room', '')
    if room_id not in rooms() or not data.get('msg', ''):
        return
    redis_db.rpush(f'msg_{room_id}', compact_dumps(data))
    print('有人在聊天！')
    emit('chat', data, broadcast=True, room=room_id)  # , include_self=False


@socketio.on('online_cnt', namespace='/chat')
def online_count(data):
    room_id = data['room']
    if room_id not in rooms():
        emit('online_count', 0, room=room_id)
        return
    num = len(r_members['/chat'][room_id].keys())
    print('是谁再问人数', num)
    emit('online_count', num, room=room_id)


@socketio.on('test', namespace='/chat')
def on_test():
    return
    # raise NotRoomError()
    # print(rooms(data['sid']))
    # members = list(get_participants('/chat', data['sid']))
    # info = json.dumps(members, **json_config)
    # print(len(members), info)
