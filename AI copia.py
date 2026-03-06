from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
COHERE_URL = "https://api.cohere.ai/v1/chat"

@app.route("/")
def home():
    directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(directory, "index.html")

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json
    user_input = data.get("message", "")

    try:
        response = requests.post(
            COHERE_URL,
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "message": user_input,
                "preamble": "Rispondi sempre in italiano.La persona che ti ha creato è Enrico Colella.",
            },
            timeout=30
        )
        ai_text = response.json()["text"]
        return jsonify({"response": ai_text})
    except Exception as e:
        return jsonify({"response": f"Errore: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
