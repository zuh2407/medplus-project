document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-text");
  const messages = document.getElementById("chatbot-messages");

  function appendMessage(sender, text) {
    const msg = document.createElement("p");
    msg.innerHTML = `<b>${sender}:</b> ${text}`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  sendBtn.addEventListener("click", () => {
    const message = input.value.trim();
    if (!message) return;

    appendMessage("You", message);
    input.value = "";

    fetch("/chatbot/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `message=${encodeURIComponent(message)}`
    })
      .then(res => res.json())
      .then(data => appendMessage("Bot", data.response))
      .catch(() => appendMessage("Bot", "Error connecting to server."));
  });
});
