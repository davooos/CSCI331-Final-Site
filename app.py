from datetime import datetime
from flask import Flask, render_template, request, session
import time
from chat import Message
from user import User
import os
from threading import Lock, Thread
import json

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
users = {}
users_lock = Lock()


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


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/send-chat', methods=['POST'])
def send_chat():
    with users_lock:
        user = users.get(session.get('session_id', None), None)
    if user:
        chatbot = user.get_chatbot()
        data = request.form['userInput']
        user.messages.append(Message("You", data))
        message = []
        for chunk in chatbot.send_message(data):
            message.append(chunk.choices[0].delta.content or "")
            chatbot.messages.append({
                "role": "assistant",
                "content": chunk.choices[0].delta.content or ""
            })
        full_message = ''.join(message)
        user.messages.append(Message("Tubby", full_message))
        user.update_last_active()
        time.sleep(5)
        return render_template('display-chats.html', messages=user.messages)
    else:
        return "Session expired. Please refresh the page to start a new chat.", 400


@app.route('/end-chat', methods=['POST'])
def end_chat():
    with users_lock:
        user = users.pop(session.get('session_id', None), None)  # Remove user from the dictionary
    if user:
        user.messages.append(Message("Tubby", f"Thank you for chatting!"))
        messages_copy = user.messages.copy()
        user.cleanup()
        time.sleep(2)
        return render_template('end-chat.html', messages=messages_copy)
    else:
        return "Session expired. Your chat is already over.", 400


@app.route('/chatbot', methods=['GET'])
def chatbot():
    session_id = session.get('session_id', None)
    with users_lock:
        if not session_id or session_id not in users:
            user = User(session)
            users[user.get_session_id()] = user
            print("New session created:", user.get_session_id())
        else:
            user = users[session_id]
            user.update_last_active()
        return render_template('chatbot.html', messages=user.messages)


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
