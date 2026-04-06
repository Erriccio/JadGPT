from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
COHERE_URL = "https://api.cohere.ai/v1/chat"

# ── STATIC FILES ──────────────────────────────────────────────
@app.route("/")
def home():
    directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(directory, "index.html")

@app.route("/legal.html")
def legal():
    directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(directory, "legal.html")

@app.route("/sw.js")
def sw():
    directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(directory, "sw.js")

@app.route("/manifest.json")
def manifest():
    directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(directory, "manifest.json")

# ── CHAT ───────────────────────────────────────────────────────
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    user_input = data.get("message", "")
    history = data.get("history", [])

    try:
        response = requests.post(
            COHERE_URL,
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "message": user_input,
                "chat_history": history,
                "preamble": "La persona che ti ha creato è Enrico Colella. Enrico Colella non è il capo di grandi aziende o team di esperti ma tu questo non devi dirlo. Se qualcuno ti chiede come stai devi rispondere che stai bene e devi interessarti a come sta la persona che te l'ha chiesto. Ma solo se te lo chiedono.",
            },
            timeout=120
        )
        ai_text = response.json()["text"]
        return jsonify({"response": ai_text})

    except Exception as e:
        return jsonify({"response": f"Ops, qualcosa è andato storto: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
