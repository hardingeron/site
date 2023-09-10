// Скрыть все сообщения через 4 секунд
setTimeout(function() {
    var messages = document.querySelectorAll('.flash');
    for (var i = 0; i < messages.length; i++) {
        messages[i].style.display = 'none';
    }
}, 6000);



// опись посылки
function openModal(inventoryData) {
  var modal = document.createElement("div");
  modal.classList.add("modal");

  var modalContent = document.createElement("div");
  modalContent.classList.add("modal-content");

  var closeBtn = document.createElement("span");
  closeBtn.classList.add("close");
  closeBtn.innerHTML = "&times;";
  closeBtn.onclick = function() {
    modal.style.display = "none";
  };

  var title = document.createElement("h3");
  title.textContent = "აღწერა";

  var inventoryText = document.createTextNode(inventoryData);
  modalContent.appendChild(title);
  modalContent.appendChild(inventoryText);
  modalContent.appendChild(closeBtn);
  modal.appendChild(modalContent);

  document.body.appendChild(modal);

  modal.style.display = "block";
}






