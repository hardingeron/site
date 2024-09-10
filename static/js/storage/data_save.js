$(document).ready(function() {
    $('#add_trecing').focus();

    // Обработка отправки формы
    $('#add-form').submit(function(event) {
        event.preventDefault(); // Остановка стандартного поведения формы

        var formData = $(this).serialize(); // Сериализация данных формы

        $.ajax({
            type: 'POST',
            url: '/save', // Путь к обработчику на сервере
            data: formData,
            success: function(response) {
                if (response.success === false) {
                    showMessage(response.message, false); // Обработка ошибки
                } else {
                    // Обработка успешного ответа от сервера
                    var lastShelf = response.last;
                    $('#add_shelf').val(lastShelf); // Устанавливаем новое значение полки
                    $('#add_trecing').val(''); // Очищаем поле текстовой области
                    $('#add_trecing').focus(); // Снова фокусируемся на текстовой области
                }
            },
            error: function() {
                console.log('Ошибка при выполнении AJAX-запроса'); // Обработка ошибки запроса
            }
        });
    });

    // Обработка ввода в текстовое поле
    $('#add_trecing').on('input', function() {
        var inputValue = $(this).val().trim(); // Получаем текущее значение поля

        // Регулярное выражение для поиска значения между "/X\" (например, /2\ или /ABC\)
        var match = inputValue.match(/\|(.*?)\\/);

        if (match) { // Если найдено совпадение
            var shelfValue = match[1]; // Получаем текст между слэшами

            // Отправляем форму, чтобы данные были сохранены
            $('#add-form').submit();

            // Используем setTimeout для задержки и установки значения shelf после отправки данных
            setTimeout(function() {
                $('#add_shelf').val(shelfValue); // Заменяем значение в поле "shelf" на найденное
            }, 900); // 100 мс задержка, можно регулировать при необходимости
        }
    });
});
