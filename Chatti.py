from app import create_app, socketio
from flask_cors import CORS


app = create_app()
CORS(app)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
