function openModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = 'flex'; /* Используем flex для центрирования */

    // Инициализация календаря с использованием flatpickr
    const datepicker = flatpickr("#datepicker", {
        dateFormat: "d-m-Y", // Формат даты
        locale: "ru", // Установка русского языка
    });

    // Добавляем обработчик события на клавишу "Esc"
    window.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });

    // Добавляем обработчик события на клик вне модального окна
    modal.addEventListener('click', function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });
}

// Функция закрытия модального окна
function closeModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = 'none';
}

// Функция перенаправления на страницу /list с выбранной датой
function redirectToPage() {
    const selectedDate = document.getElementById('datepicker').value;
    const selectedCity = document.getElementById('citySelect').value;
    
    if (selectedDate) {
        // Передаем выбранную дату и город в URL
        window.location.href = `/shipments?date=${selectedDate}&where_from=${selectedCity}`;
    }
}