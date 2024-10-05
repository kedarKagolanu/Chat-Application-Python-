// Get references to DOM elements
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

let ws; // WebSocket connection
let nickname; // User's nickname

// Function to establish WebSocket connection and set up event handlers
function connect() {
    // Prompt user for nickname
    nickname = prompt("Choose your nickname:");
    if (!nickname) {
        alert("Nickname is required!");
        return;
    }

    // Create WebSocket connection
    ws = new WebSocket('ws://localhost:55555');

    // WebSocket open event handler
    ws.onopen = () => {
        console.log('Connected to the server');
        // Send nickname to server
        ws.send(JSON.stringify({ type: 'nickname', nickname: nickname }));
    };

    // WebSocket message event handler
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        displayMessage(data.sender, data.message);
    };

    // WebSocket close event handler
    ws.onclose = () => {
        console.log('Disconnected from the server');
    };
}

// Function to display a message in the chat window
function displayMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    // Add 'sent' class if the message is from the current user, otherwise 'received'
    messageElement.classList.add(sender === nickname ? 'sent' : 'received');
    messageElement.textContent = `${sender}: ${message}`;
    chatMessages.appendChild(messageElement);
    // Scroll to the bottom of the chat window
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event listener for form submission (sending a message)
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message && ws && ws.readyState === WebSocket.OPEN) {
        // Send message to server
        ws.send(JSON.stringify({ type: 'chat', message: message }));
        messageInput.value = ''; // Clear input field
    }
});

// Initiate connection when the page loads
connect();