$(document).ready(function() {
    // Добавляем обработчик событий для кнопок удаления
    $("#recordsTable").on("click", ".deleteBtn", function() {
        // Получаем ID записи из атрибута data-record-id
        var recordId = $(this).data("record-id");

        // Отображаем всплывающее окно с подтверждением
        var confirmation = confirm("ნამდვილად გსურთ ჩანაწერის წაშლა?");

        // Если пользователь подтвердил удаление, отправляем запрос на удаление с использованием AJAX
        if (confirmation) {
            $.ajax({
                type: "POST",
                url: "/expertise_deleted",
                contentType: "application/json;charset=UTF-8",
                data: JSON.stringify({ id: recordId }),
                success: function(response) {
                    // Удаляем строку из таблицы без перезагрузки страницы
                    $("#row-" + recordId).remove();
                },
                error: function(error) {
                    console.log(error);
                }
            });
        }
    });
});

