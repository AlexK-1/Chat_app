from flask import Flask, request, render_template, redirect, url_for, flash, abort, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import send
from flask_wtf import CSRFProtect
from flask_session import Session

import os
from ast import literal_eval

from db_manager import DataBaseManager
from user_manager import User
from forms_manager import *
import events_manager as events


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
app.config['SESSION_TYPE'] = 'filesystem'

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Log in to log in to this page"

events.socketio.init_app(app)

csrf = CSRFProtect(app)

Session(app)

db = DataBaseManager("Chat.db")


@login_manager.user_loader
def load_user(user_id):
    # print("load_user")
    return User().get_user(user_id, db)

def make_login(username: str, password: str):
    user_info = db.user_get_info({"username": username}, "*", get_one=False)
    if user_info and check_password_hash(user_info[2], password):
        user_login = User().create(user_info)
        login_user(user_login, remember=True)
        session["username"] = username
        return True
    return False

# <============================== Error handlers ==============================> #
@app.errorhandler(404)
def error404(e):
    return render_template("errors/404.html")

# <============================== Index ==============================> #
@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        groups = db.rooms_user_in(current_user.get_username(), "group")
        chats = db.rooms_user_in(current_user.get_username(), "chat")
        return render_template("index_login.html", user=current_user.get_username(), groups=groups, chats=chats)
    return render_template("index_no_login.html")

# <============================== API ==============================> #
@app.route("/api/user_rooms")
def api_user_rooms():
    if current_user.is_authenticated:
        groups = db.rooms_user_in(current_user.get_username(), "group")
        chats = db.rooms_user_in(current_user.get_username(), "chat")
        response = {"successful": True,
                    "groups": groups,
                    "chats": chats}
        return jsonify(response)
    else:
        response = {"successful": False,
                    "groups": None,
                    "chats": None}
        return jsonify(response)

@app.route("/api/room_members/<int:room_id>")
def api_room_members(room_id: int):
    room = db.room_get_info({"id": room_id}, "type, members, admins, owner, visibility", False)
    if room:
        if room and room[0] != "chat":
            if (room[4] == "*all" or
                    (room[4] == "*members" and room[0] == "group" and current_user.get_username() in literal_eval(
                        room[1])) or
                    (room[0] == "archive" and current_user.get_status() == "moderator")):
                if "[" in room[1]:
                    members = literal_eval(room[1])
                else:
                    members = room[1]

                admins = literal_eval(room[2])

                response = {
                    "successful": True,
                    "is_admin": current_user.get_username() in admins,
                    "is_owner": current_user.get_username() == room[3],
                    "members": members,
                    "admins": admins,
                    "owner": room[3]
                }
                return jsonify(response)
    response = {
        "successful": False,
        "is_admin": None,
        "admins": None,
        "members": None,
        "owner": None
    }
    return jsonify(response)

@app.route("/api/room_posts/<int:room_id>")
def api_room_posts(room_id: int):
    room = db.room_get_info({"id": room_id}, "members, admins, visibility, type", False)
    if room:
        if (room[2] != "*nobody" or current_user.get_status() == "moderator") and ((room[2] == "*all" or (room[2] == "*nobody" or current_user.get_status() == "moderator")) or current_user.get_username() in literal_eval(room[0])):
            posts = db.posts_all(int(request.args.get("e")), room_id)[::-1]

            can_write = None

            response = {
                "successful": True,
                "posts": posts,
                "is_admin": current_user.get_username() in literal_eval(room[1]),
                "can_write": room[3] != "archive" and (room[0] == "*all" or current_user.get_username() in literal_eval(room[0]))
            }
            return jsonify(response)
    response = {
        "successful": False,
        "posts": None,
        "is_admin": None,
        "can_write": None
    }
    return jsonify(response)

# <============================== Room pages ==============================> #
@app.route("/rooms/<int:room_id>")
@login_required
def room(room_id: int):
    room = db.room_get_info({"id": room_id}, "*", False)
    if room:
        if ((room[3] == "archive" and current_user.get_status() == "moderator") or
                (room[3] == "chat" and (current_user.get_username() in literal_eval(room[2]))) or
                (room[3] == "group" and ((room[2] == "*all" and room[4] == "*members") or (
                        room[4] == "*members" and "[" in room[2] and current_user.get_username() in literal_eval(
                    room[2])) or room[4] == "*all"))):
            posts = db.posts_all(20, room_id)[::-1]

            if current_user.get_username() in literal_eval(room[7]):
                is_admin = True
            else:
                is_admin = False

            if room[3] == "chat":
                can_write = True

                other_chat_member = list(literal_eval(room[2]))
                other_chat_member.remove(current_user.get_username())
                other_chat_member = other_chat_member[0]

                title = f"Chat with {other_chat_member}"
            elif room[3] == "group":
                title = f"{room[1]} {room[3]}"
                if room[2] == "*all" or ("[" in room[2] and current_user.get_username() in literal_eval(room[2])):
                    can_write = True
                else:
                    can_write = False
            else:
                can_write = True
                title = f"{room[1]} {room[3]}"

            if is_admin:
                delete_form = DeleteRoomForm()
            else:
                delete_form = False

            if room[2] == "*all" or current_user.get_username() in list(literal_eval(room[2])):
                leave_form = LeaveRoomForm()
            else:
                leave_form = False

            if not can_write:
                join_form = JoinRoomForm()
            else:
                join_form = False

            print(join_form, can_write)

            return render_template("rooms/room.html", user=current_user.get_username(), room=room, posts=posts,
                                   can_write=can_write, admin=is_admin, title=title, delete_room_form=delete_form,
                                   leave_room_form=leave_form, join_room_form=join_form, can_view=True)
        else:
            return render_template("rooms/room.html", user=current_user.get_username(), room=room, posts=None,
                                   can_write=False, admin=False, title="You can't view this room.", delete_room_form=None,
                                   leave_room_form=None, join_room_form=None, can_view=False)
    else:
        abort(404)

@app.route("/rooms/<int:room_id>/delete", methods=["POST"])
@login_required
def delete_room(room_id: int):
    if db.room_exists_by_id(room_id):
        if current_user.get_username() == db.room_get_info({"id": room_id}, "owner"):
            db.room_delete(room_id)
    return redirect(url_for("index"))

@app.route("/rooms/<int:room_id>/leave", methods=["POST"])
@login_required
def leave_room(room_id: int):
    if db.room_exists_by_id(room_id):
        if current_user.get_username() in literal_eval(db.room_get_info({"id": room_id}, "members")):
            db.room_remove_member(room_id, current_user.get_username())
    return redirect(url_for("index"))

@app.route("/rooms/<int:room_id>/join", methods=["POST"])
@login_required
def join_room(room_id: int):
    if db.room_exists_by_id(room_id):
        room_data = db.room_get_info({"id": room_id}, "members, type, visibility", False)
        print(room_data[0])
        if current_user.get_username() not in literal_eval(room_data[0]) and room_data[1] == "group" and room_data[2] == "*all":
            db.room_add_member(room_id, current_user.get_username())
    return redirect(url_for("room", room_id=room_id))

@app.route("/new_room")
@login_required
def new_room():
    return render_template("rooms/new_room.html", user=current_user.get_username())

@app.route("/new_room/create", methods=["POST"])
@login_required
def create_new_room():
    if request.form.get("type") == "chat":
        if request.form.get("username") != "" and request.form.get("username") != current_user.get_username() and db.user_exists(request.form.get("username")) and not db.chat_exists(request.form.get("username"), current_user.get_username()):
            room_id = db.room_create(f"chat-{current_user.get_username()}-{request.form.get('username')}",
                           f"[\"{current_user.get_username()}\", \"{request.form.get('username')}\"]",
                           "chat",
                           "*members",
                           "",
                           f"[\"{current_user.get_username()}\", \"{request.form.get('username')}\"]")
            return redirect(url_for("room", room_id=room_id))
        else:
            flash("Probably the username.", "error")
            return redirect(url_for("new_room"))
    elif request.form.get("type") == "group":
        members = [i for i in request.form.keys() if "member_" in i and "field" not in i]
        admins = [i for i in request.form.keys() if "admin_" in i and "field" not in i]

        members = list(map(request.form.get, members))
        admins = list(map(request.form.get, admins))

        members = [i for i in members if db.user_exists(i)]
        admins = [i for i in admins if db.user_exists(i) and i in members]

        members = list(set(members))
        admins = list(set(admins))

        if request.form.get("group_name") != "":
            if len(members) > 1:
                if len(members) > 0:
                    if current_user.get_username() in members:
                        members = [f'"{i}"' for i in members]
                        admins = [f'"{i}"' for i in admins]

                        if request.form.get("open") == "open":
                            visibility = "*all"
                        else:
                            visibility = "*members"

                        room_id = db.room_create(request.form.get("group_name"),
                                       f'[{",".join(members)}]',
                                       "group",
                                       visibility,
                                       current_user.get_username(),
                                       f'[{",".join(admins)}]')

                        return redirect(url_for("room", room_id=room_id))
                    else:
                        flash("You must be a member of the group.", "error")
                else:
                    flash("There must be at least one admin in the group.", "error")
            else:
                flash("There can't be one member in a group.", "error")
        else:
            flash("Probably the name of the group.", "error")

        return redirect(url_for("new_room"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    allowed_characters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_-0123456789"
    form = SignUpForm()
    if form.validate_on_submit():
        if not db.user_exists(username=form.username.data):
            allowed = True
            for i in form.username.data.lower():
                if i not in allowed_characters:
                    allowed = False
                    break
            if allowed:
                db.user_create(form.username.data, form.password.data)  # form.email.data
                make_login(form.username.data, form.password.data)
                return redirect(url_for("index"))
            else:
                flash("For a username, you can use only letters, numbers, _ and - symbols.", "error")
        else:
            flash("Username is already in use", "error")
    return render_template("auth/signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        if make_login(form.username.data, form.password.data):
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash("Invalid username or password", "error")
    return render_template("auth/login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session["username"] = None
    return redirect(url_for("index"))


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=2200, debug=True)
    # socketio.run(app, host="127.0.0.1", port=2200, debug=True)
    events.run(app)
