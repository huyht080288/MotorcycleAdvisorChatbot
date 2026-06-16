const chatWidget = document.getElementById("chatWidget");
const chatPanel = document.getElementById("chatPanel");
const chatToggle = document.getElementById("chatToggle");
const chatMinimize = document.getElementById("chatMinimize");
const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");

function openChat() {
  chatWidget.classList.add("is-open");
  chatWidget.classList.remove("is-collapsed");
  messageInput?.focus();
}

function closeChat() {
  chatWidget.classList.remove("is-open");
  chatWidget.classList.add("is-collapsed");
}

window.openChatbot = openChat;

function appendMessage(text, role, meta = "") {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  if (meta) {
    const metaEl = document.createElement("div");
    metaEl.className = "meta";
    metaEl.textContent = meta;
    div.appendChild(metaEl);
  }
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) return;

  openChat();
  appendMessage(trimmed, "user");
  messageInput.value = "";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmed }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Lỗi kết nối");

    const meta = data.confidence
      ? `Độ tin cậy: ${(data.confidence * 100).toFixed(1)}%`
      : "";
    appendMessage(data.reply, "bot", meta);
  } catch {
    appendMessage("Không gửi được tin nhắn. Vui lòng thử lại.", "bot");
  }
}

window.askChatbot = function (question) {
  openChat();
  messageInput.value = question;
  messageInput.focus();
  sendMessage(question);
};

chatToggle?.addEventListener("click", openChat);
chatMinimize?.addEventListener("click", closeChat);

appendMessage(
  "Xin chào! Em là chatbot tư vấn của Minh Long Motor. Bạn muốn hỏi về xe, giá cả, khuyến mãi hay địa chỉ cửa hàng?",
  "bot"
);

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  await sendMessage(messageInput.value);
});

// Mở sẵn khi vào trang để luôn thấy khung chat
openChat();
