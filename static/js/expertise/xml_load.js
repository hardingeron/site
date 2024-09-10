// Добавление функции uploadFile
function uploadFile() {
    var input = document.getElementById('xmlFile');
    var file = input.files[0];
    var dateValue = document.getElementById('date').value; // Получение значения даты
    var button = document.getElementById('uploadButton'); // Получение кнопки

    // Сохранение оригинального цвета кнопки
    var originalButtonColor = button.style.backgroundColor;

        // Изменение цвета кнопки на синий и запрет ее нажатия
    button.style.backgroundColor = 'blue';
    button.disabled = true;

    var formData = new FormData();
    formData.append('xmlFile', file);
    formData.append('date', dateValue); // Добавление значения даты в formData

    $.ajax({
        url: "/rs_xml",
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            // Обработка успешного ответа от сервера
            showMessage(response.message, response.success);

            // Очистка поля с файлом
            input.value = '';

            // Перезагрузка страницы после успешного выполнения
            if (response.success) {
                window.location.reload();
            }
        },
        error: function(error) {
            // Обработка ошибки
            showMessage('Error communicating with the server', false);
        },
        complete: function() {
            // Показать кнопку после завершения запроса (в том числе после ошибки)
            button.style.backgroundColor = originalButtonColor;
            button.disabled = false;
        }
    });
}
