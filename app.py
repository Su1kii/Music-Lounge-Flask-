from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

users = {}

boy_avatars = [
    "https://avatar.iran.liara.run/public/boy?username=boy1",
    "https://avatar.iran.liara.run/public/boy?username=boy2",
    "https://avatar.iran.liara.run/public/boy?username=boy3",
]
girl_avatars = [
    "https://avatar.iran.liara.run/public/girl?username=girl1",
    "https://avatar.iran.liara.run/public/girl?username=girl2",
    "https://avatar.iran.liara.run/public/girl?username=girl3",
]
all_avatars = boy_avatars + girl_avatars


@app.route("/")
def index():
    return render_template("index.html", avatars=all_avatars)


@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000,9999)}"
    avatar_url = random.choice(all_avatars)

    users[request.sid] = {"username": username, "avatar": avatar_url}

    emit("set_username", {"username": username, "avatar": avatar_url})


@socketio.on("set_avatar")
def set_avatar(data):
    if request.sid in users:
        users[request.sid]["avatar"] = data["avatar"]


@socketio.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if user:
        emit(
            "new_message",
            {
                "username": user["username"],
                "avatar": user["avatar"],
                "message": data["message"],
            },
            broadcast=True,
        )


@socketio.on("update_username")
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["username"]
    users[request.sid]["username"] = new_username

    emit(
        "username_updated",
        {"old_username": old_username, "new_username": new_username},
        broadcast=True,
    )


@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
