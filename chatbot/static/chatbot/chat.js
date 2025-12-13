document.addEventListener('DOMContentLoaded', function () {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // Toggle Chat Window
    chatToggleBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('d-none');
        if (!chatWindow.classList.contains('d-none')) {
            chatInput.focus();
        }
    });

    // Close Chat Window
    chatCloseBtn.addEventListener('click', () => {
        chatWindow.classList.add('d-none');
    });

    // Handle Form Submission
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();

        if (message) {
            // Add User Message
            addMessage(message, 'user');
            chatInput.value = '';

            // Send to Backend
            fetch('/chat/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            })
                .then(response => response.json())
                .then(data => {
                    const botResponse = data.response || data.error || "Sorry, I couldn't understand that.";
                    addMessage(botResponse, 'bot');
                })
                .catch(error => {
                    addMessage("Error connecting to server.", 'bot');
                    console.error('Error:', error);
                });
        }
    });

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
