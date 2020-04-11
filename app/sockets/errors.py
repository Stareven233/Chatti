from .. import socketio
from .exceptions import ChatException


@socketio.on_error_default
def default_handler(e):
    if not isinstance(e, ChatException):
        return
    print('error occurred: ', e.sid)
    socketio.server._emit_internal(e.sid, 'response', str(e), namespace='/chat/rooms')
    # 主要担心它像server.call一样"not thread safe"
