document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    const addMessage = (speaker, text, messageType) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', messageType);

        const speakerElement = document.createElement('div');
        speakerElement.classList.add('speaker');
        speakerElement.innerText = speaker;

        const textElement = document.createElement('div');
        textElement.innerText = text;

        messageElement.appendChild(speakerElement);
        messageElement.appendChild(textElement);
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const sendMessage = async () => {
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        addMessage('You', messageText, 'user-message');
        userInput.value = '';

        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: messageText })
            });

            const data = await response.json();

            if (data.speaker && data.message) {
                 addMessage(data.speaker, data.message, 'bot-message');
            } else if (data.initial_discussion) {
                for (const msg of data.initial_discussion) {
                    addMessage(msg.speaker, msg.message, 'bot-message');
                }
            }

        } catch (error) {
            console.error('Error:', error);
            addMessage('System', 'Sorry, something went wrong.', 'bot-message');
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
