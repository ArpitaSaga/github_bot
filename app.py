from flask import Flask, render_template, request, jsonify
import subprocess
import json

app = Flask(__name__)

# In-memory storage (use DB or Redis later)
user_state = {}
chat_log = []  # shared messages for UI display

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()
    user_id = 'default_user'

    if user_id not in user_state:
        user_state[user_id] = {'step': 0, 'data': {}}

    state = user_state[user_id]
    step = state['step']
    data = state['data']

    chat_log.append({"sender": "user", "text": user_input})

    # Step-wise conversation logic
    if step == 0:
        bot_reply = "Hi, I am your GitHub Assistant! Do you want to fork a repository or create a pull request?"
        state['step'] = 1

    elif step == 1:
        if "fork" in user_input.lower():
            data['action'] = 'fork'
            bot_reply = "Great! Please tell me the owner's username."
            state['step'] = 2
        elif "pull" in user_input.lower():
            data['action'] = 'pull'
            bot_reply = "Let's create a pull request. Please tell me the owner's username."
            state['step'] = 2
        else:
            bot_reply = "Please type 'fork' or 'pull'."

    elif step == 2:
        data['owner'] = user_input
        bot_reply = "Got it. Now tell me the repository name."
        state['step'] = 3

    elif step == 3:
        data['repo'] = user_input
        if data['action'] == 'fork':
            bot_reply = "Please provide your GitHub token."
            state['step'] = 4
        else:
            bot_reply = "What is the head branch? (Format: your-username:branch)"
            state['step'] = 10

    # ---------- FORK FLOW ----------
    elif step == 4:
        data['token'] = user_input
        bot_reply = "Creating fork..."
        result = subprocess.run(
            ['python', 'fork_repo.py', data['owner'], data['repo'], data['token']],
            capture_output=True, text=True
        )
        bot_reply += "\n\n" + result.stdout
        state['step'] = 0
        state['data'] = {}

    # ---------- PULL REQUEST FLOW ----------
    elif step == 10:
        data['head'] = user_input
        bot_reply = "What is the base branch? (e.g., main)"
        state['step'] = 11

    elif step == 11:
        data['base'] = user_input
        bot_reply = "Please provide a title for your pull request."
        state['step'] = 12

    elif step == 12:
        data['title'] = user_input
        bot_reply = "Now add a short description for your pull request."
        state['step'] = 13

    elif step == 13:
        data['body'] = user_input
        bot_reply = "Finally, provide your GitHub token."
        state['step'] = 14

    elif step == 14:
        data['token'] = user_input
        bot_reply = "Creating your pull request..."
        result = subprocess.run(
            [
                'python', 'pull_repo.py',
                data['owner'], data['repo'],
                data['head'], data['base'],
                data['title'], data['body'], data['token']
            ],
            capture_output=True, text=True
        )
        bot_reply += "\n\n" + result.stdout
        state['step'] = 0
        state['data'] = {}

    # ---------- END ----------
    chat_log.append({"sender": "bot", "text": bot_reply})
    return jsonify({"reply": bot_reply})




@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive GitHub webhook payloads"""
    payload = request.json

    # Log it
    formatted = json.dumps(payload, indent=2)
    message = f"📦 GitHub Webhook received:\n{formatted}"

    # Show it in chat
    chat_log.append({"sender": "bot", "text": message})

    print("Received webhook event:")
    print(formatted)

    return jsonify({"status": "Webhook received"}), 200


@app.route('/messages')
def get_messages():
    """Return chat log so frontend can refresh"""
    return jsonify(chat_log)


if __name__ == '__main__':
    app.run(debug=True)
