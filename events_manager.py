from flask import request, session
from flask_socketio import SocketIO, emit
from flask_login import current_user
from flask_session import Session

from ast import literal_eval

from db_manager import DataBaseManager

socketio = SocketIO()

db = DataBaseManager("Chat.db")

def login_required(func):
    def wrapper(*args, **kwargs):
        if session["username"]:
            if db.user_exists(session["username"]):
                func(*args, **kwargs)
    return wrapper

@socketio.on("connect")
def connect_event():
    # print("Client connected")
    pass

@socketio.on("new_message")
@login_required
def message_event(data):
    room_data = db.room_get_info({"id": data["room"]}, "members")
    if data["poster"] == session["username"] and (room_data == "*all" or data["poster"] in literal_eval(room_data)):
        post_id = db.post_create(data["poster"], data["text"], data["room"])
        new_data = data.copy()
        new_data["post_id"] = post_id
        emit("new_message_created", new_data, broadcast=True)

@socketio.on("get_users_list")
def get_users_list_event(data):
    emit("send_users_list", db.users_all(data["s"], data["user"]))

@socketio.on("delete_post")
@login_required
def delete_post(data):
    room_id = db.post_get_info({"id": data["post_id"]}, "room_id")
    if db.post_exists(data["post_id"]) and (db.post_get_info({"id": data["post_id"]}, "poster") == session["username"] or db.room_user_is_admin(data["room_id"], session["username"])):
        db.post_delete(data["post_id"])
        new_data = data.copy()
        new_data["room_id"] = room_id
        emit("post_deleted", new_data, broadcast=True)

@socketio.on("promote_member")
@login_required
def promote_member(data):
    if db.room_get_info({"id": data["room_id"]}, "type") == "group":
        if not db.room_user_is_admin(data["room_id"], data["member"]) and db.room_user_is_admin(data["room_id"], session["username"]) and db.room_get_info({"id": data["room_id"]}, "owner") != data["member"]:
            db.room_add_admin(data["room_id"], data["member"])
            emit("promoted_member", data, broadcast=True)

@socketio.on("demote_admin")
@login_required
def demote_admin(data):
    if db.room_get_info({"id": data["room_id"]}, "type") == "group":
        if db.room_user_is_admin(data["room_id"], data["admin"]) and db.room_get_info({"id": data["room_id"]}, "owner") == session["username"] and db.room_get_info({"id": data["room_id"]}, "owner") != data["admin"]:
            db.room_remove_admin(data["room_id"], data["admin"])
            emit("demoted_admin", data, broadcast=True)

@socketio.on("remove_member")
@login_required
def remove_member(data):
    if db.room_get_info({"id": data["room_id"]}, "type") == "group":
        if db.room_user_is_admin(data["room_id"], session["username"]) and db.room_get_info({"id": data["room_id"]}, "owner") != data["member"]:
            db.room_remove_member(data["room_id"], data["member"])
            emit("removed_member", data, broadcast=True)


def run(app_):
    Session(app_)
    socketio.run(app_, host="127.0.0.1", port=2200, debug=True)