const chatLog = document.getElementById('chatLog');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');

function addBubble(text, who) {
  const div = document.createElement('div');
  div.className = `bubble ${who}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendMessage(text) {
  if (!text.trim()) return;
  addBubble(text, 'user');
  messageInput.value = '';
  const response = await fetch('/api/demo/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text })
  });
  const data = await response.json();
  addBubble(data.reply || 'No reply received.', 'bot');
}

chatForm.addEventListener('submit', (event) => {
  event.preventDefault();
  sendMessage(messageInput.value);
});

document.querySelectorAll('[data-msg]').forEach((button) => {
  button.addEventListener('click', () => sendMessage(button.dataset.msg));
});

addBubble('Welcome! Try: hi, menu, order, PZ01 x2, done, book, or human.', 'bot');
