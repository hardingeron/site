// Скрыть все сообщения через 2 секунд
setTimeout(function() {
    var messages = document.querySelectorAll('.flash');
    for (var i = 0; i < messages.length; i++) {
        messages[i].style.display = 'none';
    }
}, 2000);



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





// обработка кнопки редактировать
function openEditModal(number, flight) {
  const modal = document.createElement('div');
  modal.classList.add('modal');

  const modalContent = document.createElement('div');
  modalContent.classList.add('modal-content');

  const form = document.createElement('form');
  form.action = 'edit';
  form.method = 'POST';
  form.classList.add('edit_');

  const label1 = document.createElement('label');
  label1.textContent = 'ამანათის ნომერი :';
  const input1 = document.createElement('input');
    input1.type = 'text';
    input1.name = 'parcell_number';
    input1.value = number;
    input1.required = true;
    input1.readOnly = true;
    input1.style.textAlign = 'center'; // добавленный стиль
  
  const p1 = document.createElement('p');
  p1.appendChild(label1);
  p1.appendChild(input1);

  const label2 = document.createElement('label');
  label2.textContent = 'თარიღი :';

  const input2 = document.createElement('input');
  input2.type = 'text';
  input2.name = 'flight';
  input2.value = flight;
  input2.required = true;
  input2.readOnly = true;
  input2.style.textAlign = 'center'; // добавленный стиль

  const p2 = document.createElement('p');
  p2.appendChild(label2);
  p2.appendChild(input2);

  const submitButton = document.createElement('input');
  submitButton.type = 'submit';
  submitButton.value = 'რედაქტირება';
  submitButton.classList.add('edit_button');

  form.appendChild(p1);
  form.appendChild(p2);
  form.appendChild(submitButton);

  const closeButton = document.createElement('button');
  closeButton.textContent = 'X';
  closeButton.classList.add('close');

  closeButton.addEventListener('click', () => {
    document.body.removeChild(modal);
  });

  modalContent.appendChild(form);
  modalContent.appendChild(closeButton);

  modal.appendChild(modalContent);

  document.body.appendChild(modal);

  modal.style.display = 'block';
}



function openEditModal(number, flight) {
  const modal = document.createElement('div');
  modal.classList.add('modal');

  const modalContent = document.createElement('div');
  modalContent.classList.add('modal-content');

  const form = document.createElement('form');
  form.action = 'edit';
  form.method = 'POST';
  form.classList.add('edit_');

  const label1 = document.createElement('label');
  label1.textContent = 'ამანათის ნომერი :';
  const input1 = document.createElement('input');
    input1.type = 'text';
    input1.name = 'parcell_number';
    input1.value = number;
    input1.required = true;
    input1.readOnly = true;
    input1.style.textAlign = 'center'; // добавленный стиль
  
  const p1 = document.createElement('p');
  p1.appendChild(label1);
  p1.appendChild(input1);

  const label2 = document.createElement('label');
  label2.textContent = 'თარიღი :';

  const input2 = document.createElement('input');
  input2.type = 'text';
  input2.name = 'flight';
  input2.value = flight;
  input2.required = true;
  input2.readOnly = true;
  input2.style.textAlign = 'center'; // добавленный стиль

  const p2 = document.createElement('p');
  p2.appendChild(label2);
  p2.appendChild(input2);

  const submitButton = document.createElement('input');
  submitButton.type = 'submit';
  submitButton.value = 'რედაქტირება';
  submitButton.classList.add('edit_button');

  form.appendChild(p1);
  form.appendChild(p2);
  form.appendChild(submitButton);

  const closeButton = document.createElement('button');
  closeButton.textContent = 'X';
  closeButton.classList.add('close');

  closeButton.addEventListener('click', () => {
    document.body.removeChild(modal);
  });

  modalContent.appendChild(form);
  modalContent.appendChild(closeButton);

  modal.appendChild(modalContent);

  document.body.appendChild(modal);

  modal.style.display = 'block';
}