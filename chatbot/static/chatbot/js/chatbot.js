// chatbot/static/js/chatbot.js
(function() {
  const icon = document.getElementById("chatbot-icon");
  const box = document.getElementById("chatbot-box");
  const closeBtn = document.getElementById("chatbot-close");
  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-input");
  const messages = document.getElementById("chatbot-messages");

  if (!icon || !box) return; // safety check

  // Open chatbot
  icon.addEventListener("click", () => {
    box.style.display = "flex";
  });

  // Close chatbot
  closeBtn.addEventListener("click", () => {
    box.style.display = "none";
  });

  // Append messages
  function appendMessage(sender, text, color="#333") {
    const msg = document.createElement("div");
    msg.style.margin = "6px 0";
    msg.innerHTML = `<b style="color:${color}">${sender}:</b> ${text}`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  // CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      document.cookie.split(";").forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        }
      });
    }
    return cookieValue;
  }

  // Send message
  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    appendMessage("You", text, "#2563eb");
    input.value = "";
    try {
      const res = await fetch("/chatbot/", { // note: match your urls.py
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      appendMessage("Bot", data.response || "Error processing request.", "#000");
    } catch (err) {
      appendMessage("Bot", "⚠️ Connection error.", "red");
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keypress", e => { if (e.key === "Enter") sendMessage(); });

})();
