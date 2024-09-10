
function checkTrecing() {
    var trecingInput = document.getElementById('trecing_checker');
    var trecingValue = trecingInput.value;

        // Проверяем, что поле ввода не пустое
    if (trecingValue.trim() === '') {
        return;
    }

    // Используем fetch для отправки данных на сервер
    fetch('/trecing_checker', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'trecing_value=' + encodeURIComponent(trecingValue),
    })
    .then(response => response.json())
    .then(data => {
        // Определяем цвет и текст кнопки
        const result = data.result;
        const buttonColor = getButtonColor(result);
        const buttonText = getButtonText(result);

        // Выводим результат в SweetAlert2
        Swal.fire({
            text: result,
            icon: getIconByResult(result),
            timer: 4000, // 2 секунды
            showConfirmButton: true, // Показываем кнопку
            confirmButtonText: buttonText, // Текст кнопки
            confirmButtonColor: buttonColor, // Цвет кнопки
            position: isMobile() ? 'top-start' : 'center', // Позиция в зависимости от устройства
            toast: isMobile(), // Используем в режиме toast для мобильных устройств
            customClass: {
                container: 'mobile-toast-container', // Добавляем класс для стилизации
                popup: 'mobile-toast-popup' // Добавляем класс для стилизации
            }
        });

        // Очищаем поле ввода
        trecingInput.value = '';
            
        // Возвращаем фокус на поле ввода
        trecingInput.focus();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Функция для обработки события нажатия клавиши Enter
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        checkTrecing();
    }
}

// Привязываем функцию handleKeyPress к событию нажатия клавиши
document.getElementById('trecing_checker').addEventListener('keypress', handleKeyPress);

// Функция для определения цвета иконки в зависимости от результата
function getIconByResult(result) {
    switch (result) {
        case 'დაუბეგრავი!':
        case 'დაბეგვრადი დასრულებული!':
            return 'success'; // Зелёная иконка
        case 'დაბეგვრადი! არ არის მზად!':
            return 'error'; // Красная иконка
        case 'ყვითელი!':
            return 'warning'; // Жёлтая иконка
        default:
            return 'info'; // Синяя иконка
    }
}

// Функция для определения цвета кнопки в зависимости от результата
function getButtonColor(result) {
    switch (result) {
        case 'დაუბეგრავი!':
        case 'დაბეგვრადი დასრულებული!':
            return '#5cb85c'; // Зелёная кнопка
        case 'დაბეგვრადი! არ არის მზად!':
            return '#d9534f'; // Красная кнопка
        case 'ყვითელი!':
            return '#f0ad4e'; // Жёлтая кнопка
        default:
            return '#5bc0de'; // Синяя кнопка
    }
}

// Функция для определения текста кнопки в зависимости от результата
function getButtonText(result) {
    switch (result) {
        case 'დაუბეგრავი!':
            return 'გასატანი';
        case 'დაბეგვრადი დასრულებული!':
            return 'დეკლარაცია მზადაა';
        case 'დაბეგვრადი! არ არის მზად!':
            return 'დაელოდეთ დასრულებას';
        case 'ყვითელი!':
            return 'დასაბრუნებელი';
        default:
            return 'ამოუცნობი სტატუსი'; // Текст по умолчанию
    }
}

// Функция для определения, является ли устройство мобильным
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}
