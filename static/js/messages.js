// messages.js
function showMessage(message, success) {
    var messageContainer = document.getElementById("message-container");
    messageContainer.classList.remove("hidden");
    messageContainer.textContent = message;

    if (success) {
        messageContainer.classList.add("success");
    } else {
        messageContainer.classList.add("error");
    }

    messageContainer.style.display = "block";

    setTimeout(function() {
        messageContainer.style.display = "none";
        messageContainer.classList.add("hidden");
        messageContainer.classList.remove("success", "error");
    }, 3000);
}
