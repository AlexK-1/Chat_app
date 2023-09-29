from flask_socketio import SocketIO, emit

from db_manager import DataBaseManager

socketio = SocketIO()

db = DataBaseManager("Chat.db")

@socketio.on("connect")
def connect_event():
    print("Client connected")

@socketio.on("new_message")
def message_event(data):
    db.post_create(data["poster"], data["text"])
    emit("new_message", data, broadcast=True)
    print(f"New message: {data}")


def run(app):
    socketio.run(app, host="127.0.0.1", port=2200, debug=True)