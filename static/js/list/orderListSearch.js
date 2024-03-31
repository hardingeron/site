// script.js
document.addEventListener("DOMContentLoaded", function() {
    const filterInput = document.getElementById('filterInput');
    const orderList = document.getElementById('orderList');
    let items = []; // Список элементов
    let currentIndex = -1; // Индекс текущего совпадения

    // Функция для поиска следующего совпадения
    function findNextMatch(searchText) {
        // Перебираем элементы начиная с текущего индекса
        for (let i = currentIndex + 1; i < items.length; i++) {
            const item = items[i];
            const recipientFio = item.querySelector('.recipient-fio').textContent.toLowerCase();
            const recipientPhone = item.querySelector('.recipient-phone').textContent.toLowerCase();
            const passport = item.querySelector('.passport').textContent.toLowerCase();
            const senderFio = item.querySelector('.sender-fio').textContent.toLowerCase();
            const senderPhone = item.querySelector('.sender-phone').textContent.toLowerCase();

            // Если находим совпадение, устанавливаем фон и скроллим к элементу
            if (recipientFio.includes(searchText) || recipientPhone.includes(searchText) || passport.includes(searchText) || senderFio.includes(searchText) || senderPhone.includes(searchText)) {
                item.scrollIntoView({ behavior: 'smooth', block: 'start' });
                item.style.backgroundColor = 'yellow';
                setTimeout(function() {
                    item.style.backgroundColor = '';
                }, 2000);
                currentIndex = i; // Устанавливаем текущий индекс
                return true; // Возвращаем true, если нашли совпадение
            }
        }
        return false; // Возвращаем false, если совпадение не найдено
    }

    // Обработчик события нажатия на Enter
    filterInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const searchText = filterInput.value.toLowerCase().trim();
            // Если нет сохраненного списка элементов, сохраняем его
            if (items.length === 0) {
                items = Array.from(orderList.querySelectorAll('.list-group-item'));
            }
            // Если есть совпадение, ищем следующее
            if (!findNextMatch(searchText)) {
                // Если совпадение не найдено, возвращаемся к началу списка
                currentIndex = -1;
                findNextMatch(searchText);
            }
        }
    });
});