// script.js
document.addEventListener("DOMContentLoaded", function() {
    // Получаем все элементы с классом weights
    const weightsElements = document.querySelectorAll('.weights');

    // Перебираем каждый элемент
    weightsElements.forEach(weightsElement => {
        // Получаем текст из элемента
        const weightsText = weightsElement.textContent;

        // Разбиваем строку по пробелам и удаляем пустые элементы
        const weightsArray = weightsText.split(' ').filter(Boolean).map(parseFloat);

        // Вычисляем сумму всех чисел
        const sum = weightsArray.reduce((total, num) => total + num, 0);

        // Проверяем, превышает ли сумма порог
        if (sum > 29.5) {
            // Если да, добавляем класс "red"
            weightsElement.classList.add('red');
        }
    });
});