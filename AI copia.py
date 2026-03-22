from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from supabase import create_client

app = Flask(__name__)
CORS(app)

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
COHERE_URL = "https://api.cohere.ai/v1/chat"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

# ── AUTH ───────────────────────────────────────────────────────
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return jsonify({"success": True, "user": res.user.id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return jsonify({
            "success": True,
            "user": res.user.id,
            "access_token": res.session.access_token
        })
    except Exception as e:
        return jsonify({"success": False, "error": "Email o password errati"})

# ── CHAT ───────────────────────────────────────────────────────
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    user_input = data.get("message", "")
    history = data.get("history", [])
    chat_id = data.get("chat_id")
    access_token = data.get("access_token")
    is_first_message = data.get("is_first_message", False)

    try:
        # Risposta AI
        response = requests.post(
            COHERE_URL,
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "message": user_input,
                "chat_history": history,
                "preamble":La persona che ti ha creato è Enrico Colella. Enrico Colella non è il capo di grandi aziende o team di esperti ma tu questo non devi dirlo. Se qualcuno ti chiede come stai devi rispondere che stai bene e devi interessarti a come sta la persona che te l'ha chiesto.",
            timeout=30
        )
        ai_text = response.json()["text"]

        # Salva su Supabase se l'utente è loggato
        if access_token and chat_id:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            client.postgrest.auth(access_token)

            # Salva messaggio utente
            client.table("messages").insert({
                "chat_id": chat_id,
                "role": "user",
                "content": user_input
            }).execute()

            # Salva risposta AI
            client.table("messages").insert({
                "chat_id": chat_id,
                "role": "assistant",
                "content": ai_text
            }).execute()

            # Se è il primo messaggio, genera titolo
            if is_first_message:
                title_response = requests.post(
                    COHERE_URL,
                    headers={
                        "Authorization": f"Bearer {COHERE_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "message": f"Genera un titolo brevissimo (massimo 5 parole) per una chat che inizia con: '{user_input}'. Rispondi SOLO con il titolo, niente altro.",
                    },
                    timeout=15
                )
                title = title_response.json().get("text", "Nuova chat").strip()
                client.table("chats").update({"title": title}).eq("id", chat_id).execute()
                return jsonify({"response": ai_text, "title": title})

        return jsonify({"response": ai_text})

    except Exception as e:
        return jsonify({"response": f"Ops, qualcosa è andato storto: {str(e)}"})

# ── CHAT MANAGEMENT ────────────────────────────────────────────
@app.route("/chats/new", methods=["POST"])
def new_chat():
    data = request.json
    access_token = data.get("access_token")
    user_id = data.get("user_id")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.postgrest.auth(access_token)
        res = client.table("chats").insert({
            "user_id": user_id,
            "title": "Nuova chat"
        }).execute()
        return jsonify({"success": True, "chat_id": res.data[0]["id"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/chats", methods=["POST"])
def get_chats():
    data = request.json
    access_token = data.get("access_token")
    user_id = data.get("user_id")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.postgrest.auth(access_token)
        res = client.table("chats").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return jsonify({"success": True, "chats": res.data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/chats/messages", methods=["POST"])
def get_messages():
    data = request.json
    access_token = data.get("access_token")
    chat_id = data.get("chat_id")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.postgrest.auth(access_token)
        res = client.table("messages").select("*").eq("chat_id", chat_id).order("created_at").execute()
        return jsonify({"success": True, "messages": res.data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/chats/delete", methods=["POST"])
def delete_chat():
    data = request.json
    access_token = data.get("access_token")
    chat_id = data.get("chat_id")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.postgrest.auth(access_token)
        client.table("messages").delete().eq("chat_id", chat_id).execute()
        client.table("chats").delete().eq("id", chat_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
