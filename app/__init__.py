from flask import Flask
from config import Config
from flask_socketio import SocketIO
from redis import Redis
from json import dumps
from functools import partial

json_config = {'ensure_ascii': False, 'indent': None, 'separators': (',', ':')}
compact_dumps = partial(dumps, **json_config)
socketio = SocketIO()
redis_db = Redis(**Config.REDIS_URL, decode_responses=True)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins='*')
    from .main import main  # 不能在db初始化前，因为v1有用到db
    app.register_blueprint(main, url_prefix='/')
    from .api_v1 import v1
    app.register_blueprint(v1, url_prefix='/v1')
    return app
