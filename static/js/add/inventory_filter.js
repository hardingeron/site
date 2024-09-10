document.getElementById('inventory').addEventListener('input', function () {
    var maxLength = 200;
    var currentLength = this.value.length;
    var remaining = maxLength - currentLength;

    // Обновляем текст счётчика
    document.getElementById('charCount').textContent = `დარჩა ${remaining} სიმბოლო`;

    // Получаем текст без содержимого в скобках
    var text = this.value.replace(/\([^)]*\)/g, ''); // Удаляем все числа в скобках и содержимое

    // Извлекаем все числа из текста и суммируем их
    var numbers = text.match(/[-+]?[0-9]*\.?[0-9]+/g) || []; // Ищем все числа вне скобок
    var sum = numbers.reduce(function(total, num) {
        return total + parseFloat(num);
    }, 0);

    // Обновляем поле "წონა" с результатом суммы
    document.getElementById('weight').value = sum.toFixed(2); // Округляем до 2 знаков
});
