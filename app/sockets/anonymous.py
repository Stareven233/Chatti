from .. import socketio, redis_db
from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
from config import STATICS_DEST
from os import remove

get_participants = socketio.server.manager.get_participants
r_members = socketio.server.manager.rooms
# 用r_members可用于计算长度，字典类型，不可在迭代中删除键


@socketio.on('connect', namespace='/chat/rooms')
def on_connect():
    print('连接上了', request.sid)


@socketio.on('disconnect', namespace='/chat/rooms')
def on_disconnect():
    room_id = redis_db.hget(f'user_{request.sid}', 'room')
    redis_db.delete(f'user_{request.sid}')
    if room_id is None:
        return
    room_id = room_id.decode()
    room_key = f'room_{room_id}'

    if room_id in r_members['/chat/rooms']:  # 最后1人断开时socket会删去记录，此if为False
        for p in get_participants('/chat/rooms', room_id):
            disconnect(p)  # 将该用户创建房间中其他人踢出

    if redis_db.hexists(room_key, 'avatar'):
        remove(STATICS_DEST + f'\\img\\{room_key}')
    redis_db.delete(room_key, f'msg_{room_id}')  # 删除该用户创建的房间及消息记录
    print('关闭了连接', request.sid)


@socketio.on('join', namespace='/chat/rooms')
def on_join(data):
    join_room(data['room'])  # todo 考虑到client过来的可能是json，房主自己也得join
    print('有人加入了？')
    emit('online_delta', 1, broadcast=True, room=data['room'])
    emit('response', data['username'] + '加入了房间', broadcast=True, room=data['room'])


@socketio.on('leave', namespace='/chat/rooms')
def on_leave(data):
    # 在disconnect事件中调用得不到username
    leave_room(data['room'])  # todo 考虑到client过来的可能是json
    print('有人离开了？')
    emit('online_delta', -1, broadcast=True, room=data['room'])
    emit('response', data['username'] + '离开了房间', broadcast=True, room=data['room'])


@socketio.on('chat', namespace='/chat/rooms')
def on_chatting(data):  # todo 考虑到client过来的可能是json
    print('有人在聊天！')
    emit('chat', data, broadcast=True, room=data['room'])  # , include_self=False


@socketio.on('online_cnt', namespace='/chat/rooms')
def online_count(data):
    room_id = data['room']
    if not redis_db.exists(f'room_{room_id}'):
        emit('online_count', 0, room=room_id)
        return False
    num = len(r_members['/chat/rooms'][room_id].keys())
    print('是谁再问人数', num)
    emit('online_count', num, room=room_id)


@socketio.on('test', namespace='/chat/rooms')
def on_test():
    return
    # raise NotRoomError()
    # print(rooms(data['sid']))
    # members = list(get_participants('/chat/rooms', data['sid']))
    # info = json.dumps(members, **json_config)
    # print(len(members), info)
