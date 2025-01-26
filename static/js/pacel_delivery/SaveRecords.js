document.getElementById('issueButton').addEventListener('click', function () {
    // Проверяем, выбраны ли чекбоксы
    const selectedRecords = [];
    const checkboxes = document.querySelectorAll('#parcelTableBody input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const tracking = row.querySelector('td:nth-child(2)').textContent.trim();
        const recipient = row.querySelector('td:nth-child(3)').textContent.trim();
        selectedRecords.push({ tracking, recipient });
    });

    // Проверяем, выбрана ли радио-кнопка
    const citizenship = document.querySelector('input[name="citizenship"]:checked');
    if (!citizenship) {
        alert('გთხოვთ,აირჩიეთ: რეზიდენტი/არარეზიდენტი');
        return;
    }
    const isCitizen = citizenship.value === 'citizen';

    // Получаем значение паспорта
    const passport = document.getElementById('passport').value.trim();
    if (!passport) {
        alert('გთხოვთ, მიუთითეთ პასპორტი.');
        return;
    }

    // Проверяем, выбраны ли записи и передаем их на сервер
    if (selectedRecords.length === 0) {
        alert('გთხოვთ, აირჩიეთ ერთი ამანათი მაინც.');
        return;
    }

    // Формируем данные для отправки
    const dataToSend = {
        records: selectedRecords,
        citizenship: isCitizen,
        passport: passport
    };

    // Отправляем данные на сервер
    fetch('/processRecords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем статус кнопок для выбранных посылок
            selectedRecords.forEach(record => {
                // Находим строку по номеру отслеживания
                const row = Array.from(document.querySelectorAll('#parcelTableBody tr')).find(row => {
                    const trackingCell = row.querySelector('td:nth-child(2)');
                    return trackingCell && trackingCell.textContent.trim() === record.tracking;
                });

                if (row) {
                    // Находим кнопку и изменяем её статус
                    const statusButton = row.querySelector('.btn-status');
                    if (statusButton) {
                        statusButton.classList.remove('btn-danger');
                        statusButton.classList.add('btn-success');
                        statusButton.textContent = 'Выдана';
                    }
                }
            });

            // Снимаем выделение с чекбоксов
            checkboxes.forEach(checkbox => {
                checkbox.checked = false; // Снимаем выделение
            });

            alert('მონაცემები წარმატებით გადაიგზავნა!');
        } else {
            alert('მოხდა შეცდომა მონაცემების გაგზავნისას');
        }
    })
    .catch(error => console.error('Ошибка:', error));
});
