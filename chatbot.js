document.addEventListener("DOMContentLoaded", function () {
    const chatbot = document.getElementById("chatbot");
    const botUI = document.createElement("div");
    botUI.className = "chatbot-ui";
    botUI.innerHTML = `
        <div class="chat-header">Ask our bot 💬</div>
        <div class="chat-body" id="chat-body"></div>
        <input type="text" id="chat-input" placeholder="Ask about budget or sales...">
        <button onclick="sendMessage()">Send</button>
    `;
    chatbot.appendChild(botUI);
});

function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    const chatBody = document.getElementById("chat-body");

    if (message !== "") {
        const userMsg = `<div class='msg user-msg'>${message}</div>`;
        chatBody.innerHTML += userMsg;
        input.value = "";

        const reply = (message.toLowerCase().includes("budget") || message.toLowerCase().includes("sales"))
            ? "We use ML models trained on historical sales data to predict sales trends."
            : "Sorry, I can only assist with sales or budget queries.";

        const botMsg = `<div class='msg bot-msg'>${reply}</div>`;
        setTimeout(() => chatBody.innerHTML += botMsg, 500);
    }
}