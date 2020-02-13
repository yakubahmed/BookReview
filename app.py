import os

from collections import deque

from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"
socketio = SocketIO(app)

activeusers = []
channels = []
channel_messages = dict()

@app.route("/", methods=['POST','GET'])
def index():
    
    name = request.form.get('name')
    if "name" in session:
        return render_template('channels.html', channels=channels)
    
    if request.method == 'POST':
        session.clear()
        if "name" in session:
            return render_template('index.html', alert="sorry this user is all ready taken try another name")
        else:
            activeusers.append(name)
            session['name'] = name
            session.permanent = True
            return render_template('channels.html', channels=channels)
    return render_template('index.html')

@app.route("/logout")
def logout():
    # Remove from list
    try:
        activeusers.remove(session['name'])
    except ValueError:
        pass
    # Delete cookie
    session.clear()

    return redirect("/")
    
@app.route('/channels')
def chat():
    if "name" in session:
        return render_template('channels.html')
    return render_template('index.html', alert="Please login with your name first")
    

@app.route('/add channel', methods=['GET','POST'])
def add_channel():
    channel = request.form.get('channel')
    if request.method == "POST":
        if channel in channels:
            return render_template('channels.html', alert='This channel is all ready taken try another one', channels=channels)
        channels.append(channel)
        channel_messages[channel] = deque()
        return render_template('channels.html', channels=channels)
    else:
        return render_template('channels.html', channels=channels)
    return render_template('channels.html', channels=channels)
    
@app.route('/view_channel/<channel>')
def view_channel(channel):
    session['current_channel'] = channel
    if "name" in session:
        if request.method == "post":
            return redirect("/channels")
        else:
            return render_template('messages.html', channels = channels, messages=channel_messages[channel])
    else:
        return render_template('index.html')
@socketio.on("joined", namespace='/')
def joined():
    """ Send message to announce that user has entered the channel """
    
    # Save current channel to join room.
    room = session.get('current_channel')

    join_room(room)
    
    emit('status', {
        'name': session.get('name'),
        'channel': room,
        'msg': session.get('name') + ' is joined to the group <strong>' + room +"</strong>"}, 
        room=room, broadcast=True)

@socketio.on("left", namespace='/')
def left():
    """ Send message to announce that user has left the channel """

    room = session.get('current_channel')

    leave_room(room)

    emit('status', {
        'msg': session.get('name') + ' has left the channel'}, 
        room=room)

@socketio.on('send message')
def send_msg(msg, timestamp):
    """ Receive message with timestamp and broadcast on the channel """

    # Broadcast only to users on the same channel.
    room = session.get('current_channel')

    # Save 100 messages and pass them when a user joins a specific channel.

    if len(channel_messages[room]) > 100:
        # Pop the oldest message
        channel_messages[room].popleft()

    channel_messages[room].append([timestamp, session.get('name'), msg])

    emit('announce message', {
        'name': session.get('name'),
        'timestamp': timestamp,
        'msg': msg}, 
        room=room)
if __name__ == "__main__":
    app.run(debug=True)