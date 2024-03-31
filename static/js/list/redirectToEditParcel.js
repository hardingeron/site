// script.js
document.addEventListener("DOMContentLoaded", function() {
    // Получаем все элементы списка с классом list-group-item
    const listItems = document.querySelectorAll('.list-group-item');

    // Добавляем обработчик клика для каждого элемента списка
    listItems.forEach(function(item) {
        item.addEventListener('click', function() {
            // Получаем id элемента из его атрибута id
            const itemId = item.getAttribute('id');

            // Выполняем перенаправление на нужную страницу с параметром id в URL
            window.location.href = '/list_edit_id?id=' + itemId;
        });
    });
});