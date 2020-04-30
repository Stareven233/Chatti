from . import main


# @main.route('/chat/<string:room_id>')
# def chat_room(room_id):
#     return render_template('test.html')


@main.route('/img/<string:filename>')
def get_avatar(filename):
    pass
#     mime_type = redis_db.hget(f'room_{room_id}', 'avatar')
#     if not mime_type:
#         raise NotRoomError('未发现图片，房间不存在或room_id无效')
#     return send_from_directory(STATICS_DEST, f'img/room_{room_id}', mimetype=mime_type)
    # img\\room_{room_id} 反而会导致404，离谱
    # 原本打算本地文件名不保留后缀，以redis存mimetype
