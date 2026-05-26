const API = "https://jadgpt.onrender.com";
let chatHistory = [];

function mostraWelcome() {
    document.getElementById("chat").innerHTML = `
        <div id="welcome">
            <div class="welcome-badge">✦ AI Chat anonima</div>
            <div class="welcome-icon">J</div>
            <div class="welcome-title">Ciao,<br>sono JadGPT</div>
            <div class="welcome-subtitle">Chiedimi qualsiasi cosa!</div>
            <div class="suggestions">
                <button class="suggestion-btn" onclick="usaSuggerimento(this)">Cos'è l'intelligenza artificiale?</button>
                <button class="suggestion-btn" onclick="usaSuggerimento(this)">Scrivimi una poesia</button>
                <button class="suggestion-btn" onclick="usaSuggerimento(this)">Paesi più grandi del mondo?</button>
                <button class="suggestion-btn" onclick="usaSuggerimento(this)">Dammi una ricetta italiana</button>
            </div>
        </div>`;
}

mostraWelcome();

const input = document.getElementById("domanda");
const sendBtn = document.getElementById("sendBtn");

function usaSuggerimento(btn) {
    input.value = btn.textContent.slice(2).trim();
    rispondi();
}

function aggiungiMessaggio(testo, tipo) {
    const chatEl = document.getElementById("chat");

    const wrap = document.createElement("div");
    wrap.className = "msg-container " + tipo;

    const row = document.createElement("div");
    row.className = "msg-row";

    if (tipo === "bot") {
        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.textContent = "J";
        row.appendChild(avatar);
    }

    const msg = document.createElement("div");
    msg.className = "msg";

    msg.innerHTML =
        tipo === "user"
            ? escapeHTML(testo)
            : marked.parse(testo);

    row.appendChild(msg);
    wrap.appendChild(row);

    if (tipo === "bot") {
        const copyBtn = document.createElement("button");

        copyBtn.className = "copy-btn";
        copyBtn.textContent = "📋 Copia risposta";

        copyBtn.onclick = () => {
            navigator.clipboard.writeText(testo).then(() => {
                copyBtn.textContent = "✅ Copiato!";

                setTimeout(() => {
                    copyBtn.textContent = "📋 Copia risposta";
                }, 2000);
            });
        };

        wrap.appendChild(copyBtn);
    }

    const welcome = document.getElementById("welcome");

    if (welcome) welcome.remove();

    chatEl.appendChild(wrap);
    chatEl.scrollTop = chatEl.scrollHeight;
}

function escapeHTML(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function mostraTyping() {
    const chatEl = document.getElementById("chat");

    const wrap = document.createElement("div");

    wrap.className = "msg-container bot";
    wrap.id = "typing";

    wrap.innerHTML = `
        <div class="msg-row">
            <div class="avatar">J</div>
            <div class="msg">
                <div class="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;

    chatEl.appendChild(wrap);
    chatEl.scrollTop = chatEl.scrollHeight;
}

function nascondiTyping() {
    const t = document.getElementById("typing");

    if (t) t.remove();
}

async function rispondi() {
    const domanda = input.value.trim();

    if (domanda === "") return;

    aggiungiMessaggio(domanda, "user");

    input.value = "";

    mostraTyping();

    try {
        const res = await fetch(API + "/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: domanda,
                history: chatHistory
            })
        });

        const data = await res.json();

        nascondiTyping();

        aggiungiMessaggio(data.response, "bot");

        chatHistory.push({
            role: "USER",
            message: domanda
        });

        chatHistory.push({
            role: "CHATBOT",
            message: data.response
        });

    } catch {
        nascondiTyping();

        aggiungiMessaggio(
            "Ops, qualcosa è andato storto!",
            "bot"
        );
    }
}

input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        e.preventDefault();
        rispondi();
    }
});

sendBtn.addEventListener("click", rispondi);