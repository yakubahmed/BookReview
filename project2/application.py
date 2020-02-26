import os

from flask import Flask, render_template, request, jsonify, Response
import random, json, time, datetime
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)



# Arrays of channel names and registered users
channel_list = ["General"]
user_list = []

# Dictionary of users & messages
user_dm_list = {}

# dictionary to track rooms, or private channels
# Rooms = {"dn:" displayname, "room": room}
Rooms = {} 

# channel_messages = {
#    channel: chn,
#    messages: [{channel, displayname, timestamp, msg_txt}]

now = datetime.datetime.now()

startup_message = {
    "channel": "General",
    "user_from": "Flack Bot",
    "user_to": "",
    "timestamp": now.strftime("%a %b %d %I:%M:%S %Y"), 
    "msg_txt": "Welcome to Flack Messaging"}

channel_messages = {
    "General": {
        'messages': [startup_message]
}}
 
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logout", methods=["POST"])
def logout():
    return render_template("index.html")

@app.route("/flackchat", methods=["POST", "GET"])
def flackchat():
    user = request.form.get("displayname")
    return render_template("channels.html", name=user)

@app.route("/register")
def register():
    return 0

@socketio.on("submit channel")
def new_channel(data):
    channel = data["channel"]
    channel_list.append(channel)
    emit("announce channel", {"channel": channel}, broadcast=True)
    return 1

@app.route("/query_channels", methods=["POST"])
def query_channels():
    return jsonify({"success": True, "channel_list": channel_list})

@app.route("/query_users", methods=["POST"])
def query_users():
    return jsonify({"success": True, "active_users": user_list})

@app.route("/query_messages", methods=["POST"])
def fetch_messages():
    channel = request.form.get("channel")
    dn = request.form.get("displayname")
    msg_status = request.form.get("msg_type")

    if (msg_status == "PUBLIC"):
        my_msgs = channel_messages.get(channel)
    else: 
        my_msgs = user_dm_list.get(channel)

    if (my_msgs):
        msglist = my_msgs['messages']
        if ((msg_status == "PUBLIC") or (channel == dn)):
            return jsonify({"success": True, "channel_msgs": msglist})
        else:
            all_msgs = []
            for msg in msglist:
                # return only messages matching dn
                if ((msg["user_from"] == dn) or (msg['user_to'] == dn)):
                    all_msgs.append(msg)
            return jsonify({"success": True, "channel_msgs": all_msgs})
    else:
        return jsonify({"success": False, "error_msg": "No messages"})

@socketio.on("submit message")
def new_message(data):
    channel = data["channel"]
    user_from = data["user_from"]
    msg_txt = data["msg_txt"]
    timestamp = time.asctime( time.localtime( time.time() ) )


    msg = {"channel": channel, 
           "user_from": user_from, 
           "user_to": channel, 
           "timestamp": timestamp, 
           "msg_txt": msg_txt}
    if channel in channel_messages:
        # Public Channel with messages
        msgs = channel_messages[channel]
        msg["msg_type"] = "PUBLIC"
        if len(msgs['messages']) >= 100:
            del msgs['messages'][0]
        msgs['messages'].append(msg)
        emit("announce message", msg, broadcast=True)
        return jsonify ({"success": True, "msg_type": "PUBLIC"})
    else:
        if (not (channel in user_dm_list)):
            # public channel, first message
            msg["msg_type"] = "PUBLIC"
            channel_messages[channel] = {"channel": channel, "messages": [msg]}
            emit("announce message", msg, broadcast=True)
            return jsonify ({"success": True, "msg_type": "PUBLIC"})
        else: 
            # private message
            msg["msg_type"] = "PRIVATE"
            if (channel in user_dm_list):
                for user in [user_from, channel]:
                    msgs = user_dm_list[user]
                    if len(msgs['messages']) >= 100:
                        del msgs['messages'][0]
                    msgs['messages'].append(msg)
            else:
                user_dm_list[user] = {"channel": channel, "messages": [msg]}
            print (f"NM: emit msg to ", user_from)
            msg["channel"] = channel
            emit("announce message", msg, room=Rooms[user_from])
            print (f"NM: emit msg to ", channel)
            msg["channel"] = user_from
            emit("announce message", msg, room=Rooms[channel])
            return jsonify ({"success": True, "msg_type": "PRIVATE"})

@socketio.on('join')
def on_join(data):
    username = data['displayname']
    if (username == ""):
        return jsonify ({"success": False, "error_msg": "No text entered"})

    if (not (username in user_list)):
        user_list.append(username)
        user_dm_list[username] = ({"channel": username, "messages": []})
        emit("new user", {"username": username}, broadcast= True)
    else:
        emit("user logged in", {"username": username}, broadcast=True)

    room = data['room']
    join_room(room)
    Rooms[username] = room
    print (f"username ", username, "has room ", Rooms[username])
    return jsonify ({"success": True})

@socketio.on('logout user')
def on_leave(data):
    username = data['displayname']
    print (f"username ", username, " logging out")
    room = Rooms[username]
    leave_room(room)
    del Rooms[username]
    emit("user logged out", {"username": username}, broadcast=True)

@socketio.on('leave')
def on_leave(data):
    username = data['displayname']
    print (f"username ", username, " logging out")
    room = Rooms[username]
    leave_room(room)
    del Rooms[username]
    emit("user logged out", {"username": username}, broadcast=True)


if __name__ == "__main__":
    app.SECRET_KEY = "mysecret"
    app.run(debug=True)
