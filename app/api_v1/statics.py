from . import v1
from .. import redis_db
from flask import send_from_directory
from config import STATICS_DEST
from ..exceptions import NotRoomError


@v1.route('/img/<string:room_id>')
def get_room_avatar(room_id):
    mime_type = redis_db.hget(f'room_{room_id}', 'avatar')
    if not mime_type:
        raise NotRoomError('未发现图片，房间不存在或room_id无效')
    return send_from_directory(STATICS_DEST, f'img/room_{room_id}', mimetype=mime_type.decode())
    # img\\room_{room_id} 反而会导致404，离谱
