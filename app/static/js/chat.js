const SESSION_KEY = "chat_session_id";

function getSessionId() {
  return localStorage.getItem(SESSION_KEY);
}

function setSessionId(sessionId) {
  localStorage.setItem(SESSION_KEY, sessionId);
}

async function send() {
  const input = document.getElementById("question");
  const chat = document.getElementById("chat-box");
  const q = input.value.trim();
  if (!q) return;

  // user bubble
  chat.innerHTML += `<div class="bubble user">${q}</div>`;
  input.value = "";
  chat.scrollTop = chat.scrollHeight;

  // ===== bot row + loading =====
  const row = document.createElement("div");
  row.className = "chat-row";

  const avatar = document.createElement("img");
  avatar.src = "../static/images/logo_HCC.png";
  avatar.className = "bot-avatar";
  avatar.alt = "Bot";

  const bot = document.createElement("div");
  bot.className = "bubble bot";
  bot.innerText = "Đang trả lời...";

  row.appendChild(avatar);
  row.appendChild(bot);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;

  // ===== fetch =====
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      question: q,
      session_id: getSessionId()
     })
  });

  const data = await res.json();

  if (data.session_id) {
    setSessionId(data.session_id);
  }

  // 🔥 THAY THẾ loading = answer
  renderBotAnswer(bot, data);
}


function cleanAnswer(text) {
  return text.trim().replace(/\n/g, '<br>')
}

function renderBotAnswer(bot, data) {
  bot.innerHTML = ""; // xoá "Đang trả lời..."

  const text = document.createElement("div");
  text.className = "answer-text";

  const answer = cleanAnswer(data.answer);
  const hasCitations = data.citations && data.citations.length > 0;

  text.innerHTML = `
    <div class="answer-header">
      <span class="speaker"
        title="Nghe trả lời"
        onclick="playTTS(this, ${JSON.stringify(answer).replace(/"/g, '&quot;')})">
        <i class="fa-solid fa-volume-high"></i>
      </span>
    </div>

    <div class="answer-body">
      ${answer}
    </div>

    <div class="answer-toolbar left">
      <span title="Sao chép" onclick="copyAnswer(this)">
        <i class="fa-regular fa-copy"></i>
      </span>

      <span title="Thích" onclick="vote(this, 'like')">
        <i class="fa-regular fa-thumbs-up"></i>
      </span>

      <span title="Không thích" onclick="vote(this, 'dislike')">
        <i class="fa-regular fa-thumbs-down"></i>
      </span>

      ${hasCitations ? `
        <span title="Dẫn chứng"
          onclick='openPopup(${JSON.stringify(data.citations)})'>
          <i class="fa-solid fa-link"></i>
        </span>
      ` : ""}
    </div>

  `;

  bot.appendChild(text);
}

function sendFeedback(el, type, answer) {
  // bỏ active cũ
  const parent = el.parentElement;
  parent.querySelectorAll(".feedback").forEach(i => {
    i.classList.remove("active");
  });

  // active nút được chọn
  el.classList.add("active");

  // (tuỳ chọn) gửi về backend
  fetch("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type,        // like | dislike
      answer
    })
  }).catch(err => console.error(err));
}

function openPopup(citations) {
  const body = document.getElementById("popup-body");
  body.innerHTML = "";

  citations.forEach(c => {
    body.innerHTML += `
      <div style="margin-bottom:12px">
        <div style="margin-top:6px; white-space:pre-wrap; line-height: 1.6;">
          ${c.content}
        </div>
      </div>
    `;
  });

  document.getElementById("citation-popup").classList.remove("hidden");
}

function closePopup() {
  document.getElementById("citation-popup").classList.add("hidden");
}


let currentAudio = null;

async function playTTS(el, text) {
  const icon = el.querySelector("i");

  try {
    // loading
    icon.className = "fa-solid fa-spinner fa-spin";

    const res = await fetch("/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const blob = await res.blob();
    const audioUrl = URL.createObjectURL(blob);

    // stop audio cũ nếu có
    if (currentAudio) {
      currentAudio.pause();
    }

    const audio = new Audio(audioUrl);
    currentAudio = audio;

    // đang phát
    icon.className = "fa-solid fa-volume-low";

    audio.onended = () => {
      icon.className = "fa-solid fa-volume-high";
    };

    audio.onerror = () => {
      icon.className = "fa-solid fa-volume-xmark";
    };

    audio.play();

  } catch (e) {
    console.error(e);
    icon.className = "fa-solid fa-volume-xmark";
  }
}


function copyAnswer(el) {
  const answer = el.closest(".answer-text")
                   .querySelector(".answer-body").innerText;

  navigator.clipboard.writeText(answer);

  const icon = el.querySelector("i");

  // đổi icon sang check
  icon.className = "fa-solid fa-check";

  setTimeout(() => {
    icon.className = "fa-regular fa-copy";
  }, 1200);
}

function vote(el, type) {
  const toolbar = el.parentElement;
  const icon = el.querySelector("i");

  const isActive = el.classList.contains("active");

  // reset cả 2 nút
  toolbar.querySelectorAll("span").forEach(s => {
    s.classList.remove("active");
    const i = s.querySelector("i");
    if (!i) return;

    if (i.classList.contains("fa-thumbs-up")) {
      i.className = "fa-regular fa-thumbs-up";
    }
    if (i.classList.contains("fa-thumbs-down")) {
      i.className = "fa-regular fa-thumbs-down";
    }
  });

  // nếu đang active → click lần nữa thì unactive
  if (isActive) {
    // optional: gửi unvote
    sendVote(null);
    return;
  }

  // active nút mới
  el.classList.add("active");

  if (type === "like") {
    icon.className = "fa-solid fa-thumbs-up";
    sendVote("like");
  } else {
    icon.className = "fa-solid fa-thumbs-down";
    sendVote("dislike");
  }
}

function sendVote(type) {
  fetch("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type }) // type: like | dislike | null
  }).catch(() => {});
}
