from datetime import datetime
from flask import Flask, render_template, request, session
from flask_session import Session
import time
from chat import Message
from user import User
import os
from threading import Lock, Thread
import json
import redis
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
users = {}
users_lock = Lock()

redis_client = redis.StrictRedis.from_url(
    os.environ.get('REDIS_URL'),
    decode_responses=True,
    ssl_cert_reqs=None  # Disable SSL certificate verification
)

def cleanup(): # Background thread to clean up inactive sessions
    while True:
        inactive_sessions = []
        print("Running cleanup...")
        with users_lock:
            current_time = datetime.now()
            for session_id, user in list(users.items()):
                if (current_time - user.last_active).total_seconds() > 900:  # 15 minutes
                    inactive_sessions.append(session_id)

            for session_id in inactive_sessions:
                print(f"Cleaning up session: {session_id}")
                user = users[session_id]
                user.cleanup()

        time.sleep(300) # Check every 5 minutes


@app.route('/chatbot', methods=['GET'])
def chatbot():
    session_id = session.get('session_id')
    if not session_id or not redis_client.exists(session_id):
        # Create a new session
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        redis_client.hset(session_id, mapping={"messages": "[]", "last_active": str(datetime.now())})
        print("New session created:", session_id)
    else:
        # Update last active time
        redis_client.hset(session_id, "last_active", str(datetime.now()))
    messages = eval(redis_client.hget(session_id, "messages"))
    return render_template('chatbot.html', messages=messages)


@app.route('/send-chat', methods=['POST'])
def send_chat():
    session_id = session.get('session_id')
    if session_id and redis_client.exists(session_id):
        data = request.form['userInput']
        messages = eval(redis_client.hget(session_id, "messages"))
        messages.append({"sender": "You", "message": data})
        # Simulate chatbot response
        messages.append({"sender": "Tubby", "message": "This is a response."})
        redis_client.hset(session_id, "messages", str(messages))
        redis_client.hset(session_id, "last_active", str(datetime.now()))
        return render_template('display-chats.html', messages=messages)
    else:
        return "Session expired. Please refresh the page to start a new chat.", 400


@app.route('/end-chat', methods=['POST'])
def end_chat():
    session_id = session.get('session_id')
    if session_id and redis_client.exists(session_id):
        messages = eval(redis_client.hget(session_id, "messages"))
        messages.append({"sender": "Tubby", "message": "Thank you for chatting!"})
        redis_client.delete(session_id)  # Clean up session
        return render_template('end-chat.html', messages=messages)
    else:
        return "Session expired. Your chat is already over.", 400

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/catalog', methods=['GET'])
def catalog():
    json_path = os.path.join(app.static_folder, 'hot_tubs.json')
    with open(json_path, 'r') as file:
        hot_tubs = json.load(file)['hot-tubs']
    return render_template('catalog.html', tubs=hot_tubs)


@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


cleanup_thread = Thread(target=cleanup, daemon=True) # Start the cleanup thread
cleanup_thread.start()


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=os.environ.get('PORT', 5001))
