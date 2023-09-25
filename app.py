from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import os

from db_manager import DataBaseManager
from user_manager import User
from forms_manager import *


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Log in to log in to this page"

db = DataBaseManager("Chat.db")


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return User().get_user(user_id, db)

def make_login(username: str, password: str):
    user_info = db.user_get_info({"username": username}, "*", get_one=False)
    if user_info and check_password_hash(user_info[2], password):
        user_login = User().create(user_info)
        login_user(user_login, remember=True)
        return True
    return False


@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        posts = db.posts_all(20)[::-1]
        form = PostForm()
        if form.validate_on_submit():
            db.post_create(current_user.get_username(), form.text.data)
        return render_template("index_login.html", user=current_user, posts=posts, form=form)
    return render_template("index_no_login.html")

@app.route("/send", methods=["POST"])
def index_send_message():
    form = PostForm()
    if form.validate_on_submit():
        db.post_create(current_user.get_username(), form.text.data)
        return redirect(url_for("index"))

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
                db.user_create(form.username.data, form.password.data, form.email.data)
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
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2200, debug=True)
