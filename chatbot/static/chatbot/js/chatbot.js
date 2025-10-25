// chatbot/static/chatbot/js/chatbot.js
document.addEventListener("DOMContentLoaded", () => {
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

  // Toggle chat window visibility
  function openChat() {
    chatWindow.style.display = "block";
    chatWindow.setAttribute("aria-hidden", "false");
    input.focus();
  }
  function closeChat() {
    chatWindow.style.display = "none";
    chatWindow.setAttribute("aria-hidden", "true");
  }

  chatToggle.addEventListener("click", () => {
    if (chatWindow.style.display === "none" || chatWindow.style.display === "") {
      openChat();
    } else {
      closeChat();
    }
  });
  chatClose.addEventListener("click", closeChat);

  // Append message to chat box
  function appendMessage(sender, text) {
    const wrapper = document.createElement("div");
    wrapper.className = sender === "Bot" ? "bot-message" : "user-message";
    wrapper.innerHTML = `<span class="msg-sender">${sender}:</span> <span class="msg-text">${text}</span>`;
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
  }

  // Send message to backend
  function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    appendMessage("You", message);
    input.value = "";
    input.focus();

    fetch("/chatbot/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
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

  // Click handler
  sendBtn.addEventListener("click", sendMessage);

  // Enter key sends message
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

});
