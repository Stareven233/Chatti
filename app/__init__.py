from flask import Flask
from config import Config
from flask_socketio import SocketIO
from redis import Redis

socketio = SocketIO()
redis_db = Redis(**Config.REDIS_URL)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins='*')
    from .sockets import socket  # 不能在db初始化前，因为v1有用到db
    app.register_blueprint(socket, url_prefix='/socket')
    return app

