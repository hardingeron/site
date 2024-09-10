document.getElementById('downloadExcel').addEventListener('click', function() {
    // Получение значения даты, предположим, что у вас есть элемент input с id 'date'
    var dateValue = document.getElementById('date').value;

    // Создание объекта FormData для отправки данных на сервер
    var formData = new FormData();
    formData.append('date', dateValue);

    // Отправка POST-запроса на сервер для создания и скачивания файла Excel
    fetch('/expertise_export', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();  // Получаем бинарные данные
    })
    .then(blob => {
        // Создаем ссылку для скачивания
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = `expertise-${dateValue}.xlsx`;  // Имя файла для скачивания
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
});
