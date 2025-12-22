document.addEventListener('DOMContentLoaded', function () {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatMaximizeBtn = document.getElementById('chat-maximize-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // Load Messages from LocalStorage
    loadMessages();

    // Check for Checkout Success
    if (window.location.pathname === '/success/') {
        const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
        const lastMsg = history.length > 0 ? history[history.length - 1] : null;

        if (!lastMsg || !lastMsg.text.includes("Thank you for your order")) {
            addMessage("Payment received! Thank you for your order. 📦\n\nA confirmation email and invoice have been sent to your inbox. 📧\n\nIs there anything else I can help you with?", 'bot');
        }
    }

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

    // Refresh / Clear Chat
    const chatRefreshBtn = document.getElementById('chat-refresh-btn');
    if (chatRefreshBtn) {
        chatRefreshBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear the chat history?')) {
                localStorage.removeItem('chat_history');
                chatMessages.innerHTML = '';
                addMessage("Hello! How can I help you today?", 'bot', false);
            }
        });
    }

    // Toggle Maximize/Minimize
    chatMaximizeBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('maximized');
        const icon = chatMaximizeBtn.querySelector('i');
        if (chatWindow.classList.contains('maximized')) {
            icon.classList.replace('fa-expand', 'fa-compress');
            chatMaximizeBtn.title = "Minimize";
        } else {
            icon.classList.replace('fa-compress', 'fa-expand');
            chatMaximizeBtn.title = "Maximize";
        }
    });

    // Handle Form Submission
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();

        if (message) {
            // Add User Message
            addMessage(message, 'user');
            chatInput.value = '';

            // CLEAR CHAT COMMAND
            if (message.toLowerCase() === 'clear chat' || message.toLowerCase() === 'clear history') {
                localStorage.removeItem('chat_history');
                chatMessages.innerHTML = '';
                addMessage("Chat history cleared. How can I help?", 'bot');
                return;
            }

            const sessionId = getOrCreateSession();

            // Send to Backend
            fetch('/chat/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message, session_id: sessionId })
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

    // Handle File Upload
    const chatFileUpload = document.getElementById('chat-file-upload');
    if (chatFileUpload) {
        chatFileUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // 1. Show user what they uploaded
            addMessage(`📂 Uploaded: ${file.name}`, 'user');

            const sessionId = getOrCreateSession();
            const formData = new FormData();
            formData.append('file', file);
            formData.append('session_id', sessionId);

            // 2. Send to backend
            fetch('/prescription/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    // Clear input
                    chatFileUpload.value = '';

                    const botResponse = data.message || "I analyzed your file.";
                    addMessage(botResponse, 'bot');
                })
                .catch(error => {
                    addMessage("Error uploading file.", 'bot');
                    console.error('Error:', error);
                    chatFileUpload.value = '';
                });
        });
    }

    function getOrCreateSession() {
        let sessionId = localStorage.getItem('chat_session_id');
        if (!sessionId) {
            sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('chat_session_id', sessionId);
        }
        return sessionId;
    }

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

    function formatMessage(text) {
        let formatted = text;

        // 1. Headers (## Header) -> <h3>Header</h3>
        formatted = formatted.replace(/^## (.*$)/gim, '<h3>$1</h3>');

        // 2. Bold (**text**) -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

        // 2.1 Fix Wall of Text: Removed aggressive formatting that breaks lists
        // formatted = formatted.replace(/([^\n>])(<strong>)/gim, '$1<br><br>$2');

        // 2.2 Specific Button Styling for "Pay Now" or "Checkout"
        // [ Pay Now ](/checkout/) -> Button
        formatted = formatted.replace(/\[\s*(Pay Now|Checkout)\s*\]\(([^)]+)\)/gi,
            '<a href="$2" class="btn btn-success btn-sm text-white fw-bold mt-2 mb-2 shadow-sm"><i class="fa-solid fa-credit-card me-1"></i> $1</a>'
        );

        // 2.3 Generic Links [Text](URL)
        formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-primary text-decoration-underline" target="_blank">$1</a>');

        // 3. Lists
        // Split by lines to handle list logic
        let lines = formatted.split('\n');
        let inList = false;     // For <ul>
        let inNumList = false;  // For <ol>
        let result = '';

        lines.forEach(line => {
            let trimLine = line.trim();

            // Unordered List (- Item)
            if (trimLine.startsWith('- ')) {
                if (!inList) { result += '<ul>'; inList = true; }
                if (inNumList) { result += '</ol>'; inNumList = false; }
                result += `<li>${trimLine.substring(2)}</li>`;

                // Numbered List (1. Item)
            } else if (/^\d+\.\s/.test(trimLine)) {
                if (!inNumList) { result += '<ol>'; inNumList = true; }
                if (inList) { result += '</ul>'; inList = false; }
                // Remove "1. "
                let content = trimLine.replace(/^\d+\.\s/, '');
                result += `<li>${content}</li>`;

            } else {
                // Close lists if we hit normal text
                if (inList) { result += '</ul>'; inList = false; }
                if (inNumList) { result += '</ol>'; inNumList = false; }

                // Only add content if it's not empty string (prevents excess breaks from split)
                if (trimLine) {
                    result += line + '<br>';
                }
            }
        });

        if (inList) result += '</ul>';
        if (inNumList) result += '</ol>';

        return result;
    }

    function addMessage(text, sender, save = true) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        if (sender === 'bot') {
            // Render HTML for bot
            messageDiv.innerHTML = formatMessage(text);
        } else {
            // Text only for user to prevent XSS from user input
            messageDiv.textContent = text;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (save) {
            try {
                saveMessage(text, sender);
            } catch (e) {
                console.error("Storage error", e);
            }
        }
    }

    function saveMessage(text, sender) {
        const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
        history.push({ text, sender });
        // Limit history to 50 messages
        if (history.length > 50) history.shift();
        localStorage.setItem('chat_history', JSON.stringify(history));
    }

    function loadMessages() {
        const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
        // Don't save again when loading
        history.forEach(msg => {
            addMessage(msg.text, msg.sender, false);
        });

        if (history.length === 0) {
            // Show welcome message if empty
            addMessage("Hello! How can I help you today?", 'bot', false);
        }
    }
});
