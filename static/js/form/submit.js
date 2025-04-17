const form = document.getElementById('parcel-form');
let pendingFormData = null;

form.addEventListener('submit', function (e) {
  e.preventDefault();

  // Получаем поля и значения
  const senderPhoneEl = document.getElementById('sender_phone');
  const recipientPhoneEl = document.getElementById('recipient_phone');
  const senderPhone = senderPhoneEl.value.trim();
  const recipientPhone = recipientPhoneEl.value.trim();
  const messageArea = document.getElementById('message-area');
  messageArea.innerHTML = '';

  // Проверка отправителя
  if (senderPhone.length !== 12) {
    showError('Номер отправителя указан неверно. Проверьте и попробуйте снова.', senderPhoneEl);
    return;
  }

  // Проверка получателя
  if (recipientPhone.length !== 13) {
    showError('Номер получателя указан неверно. Проверьте и попробуйте снова.', recipientPhoneEl);
    return;
  }

  // Всё ок — сохраняем данные и показываем модалку
  pendingFormData = new FormData(form);
  const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
  confirmModal.show();
});

document.getElementById('confirmSubmitBtn').addEventListener('click', function () {
  if (!pendingFormData) return;

  fetch('/submit-parcel', {
    method: 'POST',
    body: pendingFormData
  })
    .then(res => res.json())
    .then(data => {
      const messageArea = document.getElementById('message-area');
      messageArea.innerHTML = '';

      if (data.status && data.message) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${data.status} alert-dismissible fade show mt-3`;
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
          ${data.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
        `;
        messageArea.appendChild(alert);
      }

      if (data.status === 'success') {
        form.querySelectorAll('input, textarea, select, button').forEach(el => {
          el.disabled = true;
        });
      }

      const confirmModalEl = document.getElementById('confirmModal');
      const modal = bootstrap.Modal.getInstance(confirmModalEl);
      modal.hide();

      pendingFormData = null;
    })
    .catch(err => {
      console.error('Ошибка:', err);
    });
});

// Функция показа ошибки + подсветка поля
function showError(message, inputElement) {
  const messageArea = document.getElementById('message-area');

  const alert = document.createElement('div');
  alert.className = `alert alert-danger alert-dismissible fade show mt-3`;
  alert.setAttribute('role', 'alert');
  alert.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
  `;
  messageArea.appendChild(alert);

  // Подсветка поля
  inputElement.classList.add('is-invalid');
  setTimeout(() => {
    inputElement.classList.remove('is-invalid');
  }, 5000);
}
