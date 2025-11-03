// chatbot/static/chatbot/js/chatbot.js
(function () {
  const icon = document.getElementById('chatbot-icon');
  const box = document.getElementById('chatbot-box');
  const closeBtn = document.getElementById('chatbot-close');
  const sendBtn = document.getElementById('chatbot-send');
  const input = document.getElementById('chatbot-input');
  const messages = document.getElementById('chatbot-messages');

  if (!icon || !box || !sendBtn || !input || !messages) {
    console.warn('Chatbot: missing DOM elements, widget disabled.');
    return;
  }

  function openChat() {
    box.style.display = 'flex';
    box.setAttribute('aria-hidden', 'false');
    input.focus();
    scrollToBottom();
  }

  function closeChat() {
    box.style.display = 'none';
    box.setAttribute('aria-hidden', 'true');
  }

  function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  function appendMessage(text, sender='bot') {
    const container = document.createElement('div');
    container.className = sender === 'user' ? 'user-message' : 'bot-message';
    if (sender === 'user') container.innerText = text;
    else container.innerHTML = text;
    messages.appendChild(container);
    scrollToBottom();
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    appendMessage(text, 'user');
    input.value = '';

    const loading = document.createElement('div');
    loading.className = 'bot-message';
    loading.textContent = '⏳ Looking up...';
    messages.appendChild(loading);
    scrollToBottom();

    const endpoint = window.CHATBOT_ENDPOINT || '/chatbot/get_response/';

    try {
      const resp = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (loading && loading.parentNode) loading.remove();

      if (!resp.ok) {
        appendMessage("Sorry, I couldn't reach the server. Please try again later.", 'bot');
        return;
      }

      const data = await resp.json();
      appendMessage(data.response || "I didn't get anything back.", 'bot');
    } catch (err) {
      if (loading && loading.parentNode) loading.remove();
      appendMessage("Network error. Please check your connection.", 'bot');
      console.error('Chatbot send error', err);
    }
  }

  icon.addEventListener('click', () => {
    if (box.style.display === 'flex') closeChat();
    else openChat();
  });

  closeBtn.addEventListener('click', closeChat);
  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
  });

  closeChat();
})();
