from .. import socketio, redis_db, compact_dumps
from flask_socketio import emit, join_room, leave_room, disconnect, rooms, Namespace
from flask import request
from config import STATICS_DEST
from os import remove


get_participants = socketio.server.manager.get_participants
r_members = socketio.server.manager.rooms
# r_members[][]: 获取房间成员，可用于计算长度，字典类型，不可在迭代中删除键
# get_participants(, ): 获取房间成员，生成器；room_id不正确则报错，为None则返回所有用户


class ChatRoom(Namespace):
    def __init__(self, namespace):
        super().__init__(namespace)

    def on_connect(self):
        emit('sid', request.sid, room=request.sid)
        print('连接上了', request.sid)

    def on_disconnect(self):
        rm_list = [f'user_{request.sid}']  # user_key
        room_id = redis_db.hget(rm_list[0], 'room')

        if room_id:  # 非房主不会有room_id
            for p in get_participants('/chat', room_id):
                if p != request.sid:
                    disconnect(p)  # 触发该事件时房主已断开，故只需断开其他人即可
            rm_list.append(f'room_{room_id}')  # room_key
            rm_list.append(f'msg_{room_id}')  # msg_key

        for k in rm_list[:2]:
            avatar = redis_db.hget(k, 'avatar')
            if not avatar:
                continue
            remove(STATICS_DEST + f'/img/{avatar}')

        redis_db.delete(*rm_list)
        print('关闭了连接', request.sid)

    def on_join(self, data):
        room_id = data.pop('room', '')
        if not redis_db.exists(f'room_{room_id}'):
            return
        join_room(room_id)  # 房主自己也得join
        print('有人加入了？')
        # emit('online_delta', 1, broadcast=True, room=room_id)
        emit('response', data['name'] + '加入了房间', broadcast=True, room=room_id)

    def on_leave(self, data):
        room_id = data.pop('room', '')
        if room_id not in rooms():
            return
        leave_room(room_id)
        print('有人离开了？')
        # emit('online_delta', -1, broadcast=True, room=room_id)
        num = len(r_members['/chat'][room_id].keys())
        emit('online_count', num, room=room_id)  # 原本应由前端根据事件将人数减一
        emit('response', data['name'] + '离开了房间', broadcast=True, room=room_id)

    def on_chat(self, data):
        room_id = data.pop('room', '')
        if room_id not in rooms() or not data.get('msg', ''):
            return
        redis_db.rpush(f'msg_{room_id}', compact_dumps(data))
        print('有人在聊天！')
        emit('chat', data, broadcast=True, room=room_id)  # , include_self=False

    def on_online_cnt(self, data):
        room_id = data['room']
        if room_id not in rooms():
            emit('online_count', 0, room=room_id)
            return
        num = len(r_members['/chat'][room_id].keys())
        print('是谁再问人数', num)
        emit('online_count', num, room=room_id)


socketio.on_namespace(ChatRoom('/chat'))
