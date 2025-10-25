document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-text");
  const messages = document.getElementById("chat-box");
  const chatToggle = document.getElementById("chat-toggle");
  const chatWindow = document.getElementById("chat-window");

  // Toggle chat window visibility
  chatToggle.addEventListener("click", () => {
    if (chatWindow.style.display === "none" || chatWindow.style.display === "") {
      chatWindow.style.display = "block";
      input.focus();
    } else {
      chatWindow.style.display = "none";
    }
  });

  function appendMessage(sender, text) {
    const msg = document.createElement("div");
    msg.className = sender === "Bot" ? "bot-message" : "user-message";
    msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    appendMessage("You", message);
    input.value = "";

    fetch("/chatbot/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `message=${encodeURIComponent(message)}`
    })
      .then(res => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
      })
      .then(data => {
        appendMessage("Bot", data.response);
      })
      .catch(() => appendMessage("Bot", "Error connecting to server."));
  }

  // Click handler
  sendBtn.addEventListener("click", sendMessage);

  // Enter key submits
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });
});
