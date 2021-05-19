from flask import render_template, jsonify, session, request
import uuid
from init import app, socketio
from controller import LogWatcher
import time
from flask_socketio import join_room

@app.route('/startWatcher', methods=['POST'])
def startWatcher():
    print("In startwatcher")
    LogWatcher.stop_signal = 0
    return jsonify({'msg':'watcher started'})

#To launch the observer
@app.route('/execWatcher', methods=['GET', 'POST'])
def execWatcher():
    print("In execWatcher")
    LogWatcher.stop_signal = 0

    logWatcher = LogWatcher(  watchDirectory = (request.form['inpFolder'] if request.form['inpFolder'] else app.config['WATCH_DIRECTORY'])
                            , watchDelay = app.config['WATCH_DELAY']
                            , watchRecursively = app.config['WATCH_RECURSIVELY']
                            , watchPattern = app.config['WATCH_PATTERN']
                            , exceptionPattern = app.config['EXCEPTION_PATTERN']
                            , sessionid = session['uid']
                            , namespace='/logWatcher'
                            )
    logWatcher.run()
    info = logWatcher.info()
    return jsonify(info)

#To stop the observer
@app.route('/stopWatcher', methods=['POST'])
def stopWatcher():
    print("In stopWatcher")
    LogWatcher.stop_signal = 1
    time.sleep(2)
    return jsonify({'msg':'watcher stopped'})


@app.route("/", methods=['GET'])
def index():
    # create a unique session ID and store it within the Flask session
    if 'uid' not in session:
        sid = str(uuid.uuid4())
        session['uid'] = sid
        print("Session ID stored =", sid)
    return render_template('index.html')


@socketio.on('connect', namespace='/logWatcher')
def socket_connect():
    # Display message upon connecting to the namespace
    print('Client Connected To NameSpace /logWatcher - ', request.sid)


@socketio.on('disconnect', namespace='/logWatcher')
def socket_connect():
    # Display message upon disconnecting from the namespace
    print('Client disconnected From NameSpace /logWatcher - ', request.sid)


@socketio.on('join_room', namespace='/logWatcher')
def on_room():
    room = str(session['uid'])
    # Display message upon joining a room specific to the session previously stored.
    print(f"Socket joining room {room}")
    join_room(room)


@socketio.on_error_default
def error_handler(e):
    # Display message on error.
    print(f"socket error: {e}, {str(request.event)}")


if __name__ == "__main__":
    # app.run(debug = True)
    socketio.run(app, debug=True)


