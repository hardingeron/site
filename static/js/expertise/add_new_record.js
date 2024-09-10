$(document).ready(function() {
    $("#addRecordBtn").click(function() {
        // Получаем данные из полей ввода
        var number = $("#Number").val();
        var tracking = $("#tracking").val();
        var comment = $("#comment").val();
        var date = $("#date").val();

        // Создаем объект данных для отправки на сервер
        var data = {
            Number: number,
            tracking: tracking,
            comment: comment,
            date: date
        };

        // Отправляем данные на сервер с использованием AJAX
        $.ajax({
            type: "POST",
            url: "/expertise_add_record",
            contentType: "application/json;charset=UTF-8",
            data: JSON.stringify(data),
            success: function(records) {
                // Проверяем структуру ответа
                console.log('Response from server:', records);
                    
                // Проверяем, что `records` является массивом
                if (Array.isArray(records)) {
                    // Выводим сообщение об успешном добавлении записей
                    showMessage('ამანათი წარმატებით დაემატა', true);

                    // Создаем строки для каждой записи
                    records.forEach(function(response) {
                        // Создаем уникальный ID для строки
                        var rowId = 'row-' + response.id;

                        // Определение класса цвета в зависимости от значения статуса
                        var statusColorClass = '';
                        if (response.status === 'დაუბეგრავი') {
                            statusColorClass = 'დაუბეგრავი';
                        } else if (response.status === 'დაბეგვრადი') {
                            statusColorClass = 'დაბეგვრადი';
                        } else if (response.status === 'გაურკვეველი') {
                            statusColorClass = 'გაურკვეველი';
                        }

                            // Создание строки таблицы с добавлением класса цвета
                        var newRow = '<tr id="' + rowId + '" class="table_values">' +
                            '<td>' + response.id + '</td>' +
                            '<td class="status_color ' + statusColorClass + '">' + response.status + '</td>' +
                            '<td>' + response.recipient + '</td>' +
                            '<td>' + response.weight + '</td>' +
                            '<td>' + response.Number + '</td>' +
                            '<td>' + response.tracking + '</td>' +
                            '<td>' + response.comment + '</td>' +
                            '<td>' + response.date + '</td>' +
                            '<td><button class="btn btn-danger btn-sm deleteBtn" data-record-id="' + response.id + '">წაშლა</button></td>' +
                            '</tr>';
                            
                        // Добавляем новую запись к таблице
                        $("#recordsTable tbody").append(newRow);
                    });

                    // Очищаем поля ввода после успешного добавления
                    $("#Number").val('');
                    $("#tracking").val('');
                    $("#comment").val('');
                    $("#date").val('');
                } else {
                    // Выводим сообщение об ошибке если `records` не является массивом
                    showMessage('Некорректный формат данных', false);
                }
            },
            error: function(xhr, status, error) {
                // Выводим сообщение об ошибке
                showMessage('ამანათი ვერ დამუშავდა!', false);
            }
        });
    });
});
