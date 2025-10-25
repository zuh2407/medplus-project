// chatbot/static/chatbot/js/chatbot.js
document.addEventListener("DOMContentLoaded", () => {
  // Find widget container and elements safely
  const widget = document.getElementById("pharmacy-chatbot-widget");
  if (!widget) return; // no widget on this page

  const endpoint = widget.dataset.endpoint || "/chatbot/";

  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-text");
  const messages = document.getElementById("chat-box");
  const chatToggle = document.getElementById("chat-toggle");
  const chatWindow = document.getElementById("chat-window");
  const chatClose = document.getElementById("chat-close");

  // Helper: get cookie (for CSRF)
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  const csrftoken = getCookie('csrftoken');

  // Toggle chat window visibility (safe)
  function openChat() {
    if (!chatWindow) return;
    chatWindow.style.display = "block";
    chatWindow.setAttribute("aria-hidden", "false");
    if (input) input.focus();
  }
  function closeChat() {
    if (!chatWindow) return;
    chatWindow.style.display = "none";
    chatWindow.setAttribute("aria-hidden", "true");
  }

  if (chatToggle) {
    chatToggle.addEventListener("click", () => {
      if (!chatWindow) openChat(); // fallback
      if (chatWindow.style.display === "none" || chatWindow.style.display === "") {
        openChat();
      } else {
        closeChat();
      }
    });
  }

  if (chatClose) chatClose.addEventListener("click", closeChat);

  // Append message to chat box
  function appendMessage(sender, text) {
    if (!messages) return;
    const wrapper = document.createElement("div");
    wrapper.className = sender === "Bot" ? "bot-message" : "user-message";
    // allow HTML (bot responses may include simple markup from server)
    wrapper.innerHTML = `<span class="msg-sender">${sender}:</span> <span class="msg-text">${text}</span>`;
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
  }

  // Send message to backend
  function sendMessage() {
    if (!input) return;
    const message = input.value.trim();
    if (!message) return;

    appendMessage("You", message);
    input.value = "";
    input.focus();

    // try sending as form-encoded (server accepts form); include CSRF header
    fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-CSRFToken": csrftoken || ''
      },
      body: `message=${encodeURIComponent(message)}`
    })
    .then(res => {
      if (!res.ok) throw new Error('Network response not ok');
      return res.json();
    })
    .then(data => {
      const botText = data && data.response ? data.response : "No response.";
      appendMessage("Bot", botText);
    })
    .catch((err) => {
      console.error("Chatbot error:", err);
      appendMessage("Bot", "Error connecting to server.");
    });
  }

  // Attach send handlers (defensive - check elements exist)
  if (sendBtn) {
    sendBtn.addEventListener("click", sendMessage);
  }
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    });
  }
});
