from app import create_app, socketio
from flask import render_template


app = create_app()


@app.route('/')
def index():
    return render_template('test.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)
