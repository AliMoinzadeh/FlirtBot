document.getElementById('getSample').addEventListener('click', () => {
    sendTextToBackend("get_sample", document.getElementById('chatField').value);
});

document.getElementById('getResponse').addEventListener('click', () => {
    sendTextToBackend("get_response_with_memory", document.getElementById('chatField').value);
});

document.getElementById('chatField').addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        sendTextToBackend("get_response_with_memory", document.getElementById('chatField').value);
    }
});

document.getElementById('reset').addEventListener('click', () => {
    resetHistory();
});

document.getElementById('loadFromMemory').addEventListener('click', () => {
    updateHistory();
});

document.getElementById('loadFromFile').addEventListener('click', () => {
    getChatHistoryFromFiles(document.getElementById('filenameField').value);
});

base_url = "http://localhost:5000/";

function sendTextToBackend(method, text) {
    fetch(base_url + method, {
        method: 'POST',
        body: text,
        headers: {
            'Content-Type': 'text',
        },
    })
    .then(response => {
        return response.json()
    })
    .then(data => {
        document.getElementById('backendResponse').textContent = `${data.response}`;
        // TODO clear content of chatField
        document.getElementById('chatField').value = "";
    })
    .then(() => {
        updateHistory();
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Simulating a delay as if calling the backend
    setTimeout(() => {
        const simulatedResponse = "still waiting for a response...";
        document.getElementById('backendResponse').textContent = `${simulatedResponse}`;
    }, 1000); // Simulate a network delay of 1 second
}

function resetHistory() {
    fetch(base_url + 'reset_chat_history', {
        method: 'POST',
        body: "",
        headers: {
            'Content-Type': 'text',
        },
    })
    .then(_ => {
        document.getElementById('backendResponse').textContent = "";
        document.getElementById('chatField').textContent = "";
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateHistory() {
    fetch(base_url + 'get_chat_history')
    .then(response => {
        return response.json()
    })
    .then(data => {
        renderChatHistory(data.chat_history);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getChatHistoryFromFiles(filename) {
    fetch(base_url + 'load_chat_history_from_files', {
        method: 'POST',
        body: filename,
        headers: {
            'Content-Type': 'text',
        },
    })
    .then(response => {
        return response.json()
    })
    .then(data => {
        renderChatHistory(data.chat_history);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function renderChatHistory(chatHistory) {
    // Update the chat history
    const chatHistoryElement = document.getElementById('chatHistory');
    // Clear the existing content
    chatHistoryElement.innerHTML = '';
    // Render each item as a list element
    chatHistory.forEach(item => {
        const listItem = document.createElement('li');
        listItem.textContent = item.user + ": " + item.content;
        chatHistoryElement.appendChild(listItem);
    });
    // Scroll to the bottom of the chat history
    // chatHistoryElement.scrollTop = chatHistoryElement.scrollHeight;
}
