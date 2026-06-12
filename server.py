from flask import Flask, render_template, request, jsonify
from agent import ask
from memory import load_history

app = Flask(__name__)
history = load_history()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def get_history():
    return jsonify(history)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    reply = ask(user_message, history)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
