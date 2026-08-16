const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

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

function appendMessage(text, cls) {

    const div = document.createElement("div");

    div.className = cls;

    div.innerHTML =
    `
        ${text}
        <span class="time">${getCurrentTime()}</span>
    `;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;

}

async function sendMessage() {

    const message = input.value.trim();

    if(message === "") return;

    appendMessage(message,"user-message");

    input.value="";

    sendBtn.innerHTML="⏳";

    const typing=document.createElement("div");

    typing.className="bot-message";

    typing.id="typing";

    typing.innerHTML=
    `
        Typing...
        <span class="time">${getCurrentTime()}</span>
    `;

    chatBox.appendChild(typing);

    chatBox.scrollTop=chatBox.scrollHeight;

    try{

        const response=await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                message:message
            })

        });

        const data=await response.json();

        typing.remove();

        appendMessage(data.reply,"bot-message");

    }

    catch(error){

        typing.remove();

        appendMessage(
            "Unable to connect to server.",
            "bot-message"
        );

    }

    sendBtn.innerHTML="🎤";

}

function quickMessage(message){

    input.value=message;

    sendMessage();

}

input.addEventListener("keypress",function(event){

    if(event.key==="Enter"){

        sendMessage();

    }

});

window.onload=function(){

    chatBox.scrollTop=chatBox.scrollHeight;

    input.focus();

};