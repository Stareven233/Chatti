from .. import socketio
from ..exceptions import MyApiError


@socketio.on_error_default
def default_handler(e):
    if not isinstance(e, MyApiError):
        return
    # print('error occurred: ', e.sid)
    socketio.server._emit_internal(e.sid, 'error', e.to_json(), namespace='/chat/rooms')
    # 主要担心它像server.call一样"not thread safe"
