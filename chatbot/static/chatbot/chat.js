document.addEventListener('DOMContentLoaded', function () {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatMaximizeBtn = document.getElementById('chat-maximize-btn');
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

    function formatMessage(text) {
        let formatted = text;

        // 1. Headers (## Header) -> <h3>Header</h3>
        formatted = formatted.replace(/^## (.*$)/gim, '<h3>$1</h3>');

        // 2. Bold (**text**) -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

        // 2.1 Fix Wall of Text: Add breaks before specific bold headers to ensure spacing
        // We look for <strong> tags that likely represent sections (Indications, Warnings, etc)
        formatted = formatted.replace(/([^\n>])(<strong>)/gim, '$1<br><br>$2');

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

    function addMessage(text, sender) {
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
    }
});
