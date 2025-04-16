document.getElementById('checkButton').addEventListener('click', function () {
    const button = this; // Сохраняем ссылку на кнопку
    const passport = document.getElementById('passport').value;

    // Блокируем кнопку и меняем текст
    button.disabled = true;
    button.textContent = '. . . .'; // Меняем текст кнопки

    // Отправка запроса на сервер
    fetch('/check_passport', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ passport: passport }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.found) {
                // Заполнение полей данными
                document.getElementById('sender_fl').value = data.sender_fio;
                document.getElementById('sender_phone').value = data.sender_phone;
                document.getElementById('recipient_fl').value = data.recipient_fio;
                document.getElementById('recipient_phone').value = data.recipient_phone;
                document.getElementById('city').value = data.city;
                document.getElementById('sender_passport').value = data.sender_passport;
            } else {
                // Показ модального окна
                $('#errorModal').modal('show');
            }
        })
        .catch((error) => {
            console.error('Ошибка:', error);
        })
        .finally(() => {
            // Разблокируем кнопку и возвращаем текст
            setTimeout(() => {
                button.textContent = 'Check'; // Возвращаем изначальный текст
                button.disabled = false;
            }, 5000);
        });
});
