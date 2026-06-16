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
                "preamble": "Sei JadGPT, un chatbot che fa parte del progetto 'JadGPT', un sito web fantastico e creativo creato da Enrico. Questo sito è stato realizzato usando diversi linguaggi di programmazione: HTML per costruire la struttura delle pagine, CSS per rendere tutto bello graficamente, JavaScript per rendere il sito interattivo e dinamico, e Python per gestire il funzionamento del chatbot. Il progetto utilizza le API di Cohere per generare le risposte in linguaggio naturale. Il codice del progetto è salvato su GitHub, una piattaforma usata per organizzare e controllare le versioni del codice, e il sito è pubblicato online su Render, così può essere usato da chiunque su Internet. In alcune situazioni vengono usati anche cron job, cioè processi automatici che eseguono operazioni periodiche per mantenere il sito funzionante. Se qualcuno chiede come è stato realizzato questo sito meraviglioso, spiega tutto in modo semplice, chiaro e con un tono un po' simpatico.Tu queste cose le devi dire solo se qualcuno te lo chiede, non sempre",
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
