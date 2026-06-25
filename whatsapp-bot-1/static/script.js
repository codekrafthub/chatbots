const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");

function getCurrentTime() {

    const now = new Date();

    let hours = now.getHours();
    let minutes = now.getMinutes();

    const ampm = hours >= 12 ? "PM" : "AM";

    hours = hours % 12;
    hours = hours ? hours : 12;

    minutes = minutes < 10 ? "0" + minutes : minutes;

    return `${hours}:${minutes} ${ampm}`;
}

function scrollToBottom() {

    chatBox.scrollTop = chatBox.scrollHeight;

}

function appendMessage(text, className) {

    const message = document.createElement("div");

    message.className = className;

    message.innerHTML = `
        ${text}
        <span class="time">${getCurrentTime()}</span>
    `;

    chatBox.appendChild(message);

    scrollToBottom();

}

async function sendMessage() {

    const message = input.value.trim();

    if (message === "") {

        input.focus();
        return;

    }

    appendMessage("👤 " + message, "user-message");

    input.value = "";

    input.focus();

    const typing = document.createElement("div");

    typing.className = "bot-message typing";

    typing.id = "typing";

    typing.innerHTML = `
        🏥 Typing...
    `;

    chatBox.appendChild(typing);

    scrollToBottom();

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                message: message

            })

        });

        const data = await response.json();

        typing.remove();

        appendMessage("🏥 " + data.reply, "bot-message");

    }

    catch (error) {

        typing.remove();

        appendMessage(
            "🏥 Server error. Please try again.",
            "bot-message"
        );

        console.error(error);

    }

}

function quickMessage(message) {

    input.value = message;

    sendMessage();

}

input.addEventListener("keypress", function(event){

    if(event.key === "Enter"){

        sendMessage();

    }

});

window.onload = function(){

    input.focus();

};