// script.js
function manifestDownload() {
    // Получаем строку запроса из текущего URL
    var queryString = window.location.search;

    // Создаем объект URLSearchParams из строки запроса
    var urlParams = new URLSearchParams(queryString);

    // Извлекаем значения параметров из URL
    var date = urlParams.get('date');
    var where_from = urlParams.get('where_from');

    // Показываем всплывающее окно с подтверждением
    var userConfirmed = confirm("თქვენ მართლა გსურთ მანიფესტის გადმოწერა? თუ არ იცით რას აკეთეთ გთხოვთ გააუქმოთ!!!");

    // Если пользователь подтвердил, отправляем запрос на сервер Flask
    if (userConfirmed) {
        var downloadUrl = `/download_manifest?date=${date}&where_from=${where_from}`;

        // Создаем временную ссылку для скачивания файла
        var a = document.createElement('a');
        a.href = downloadUrl;

        // Задаем имя файла
        a.download = 'manifest.xlsx';

        // Добавляем элемент в DOM и эмулируем клик для скачивания файла
        document.body.appendChild(a);
        a.click();

        // Удаляем элемент из DOM
        document.body.removeChild(a);
    }

    // Перезагружаем страницу после задержки 2 секунды
    setTimeout(function() {
        window.location.reload();
    }, 2000);
}