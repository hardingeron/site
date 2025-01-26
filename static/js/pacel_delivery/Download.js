document.getElementById('downloadExcelButton').addEventListener('click', function () {
    // Отправляем запрос на сервер для получения Excel файла
    fetch('/downloadExcel', {
        method: 'POST',  // Используем метод POST
        headers: {
            'Content-Type': 'application/json',  // Указываем, что это JSON-запрос
        },
    })
    .then(response => {
        if (response.ok) {
            // Если запрос успешен, создаем ссылку для скачивания
            return response.blob();  // Получаем файл как Blob
        } else {
            throw new Error('მოხდა შეცდომა მონაცემების გადმოწერისას');
        }
    })
    .then(blob => {
        // Создаем ссылку для скачивания
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'data.xlsx';  // Имя файла
        document.body.appendChild(a);
        a.click();
        a.remove();  // Удаляем временную ссылку
    })
    .catch(error => {
        alert('Ошибка: ' + error.message);  // Показать ошибку в случае неудачи
    });
});
