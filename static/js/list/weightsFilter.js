function weightsInputHandler(input) {
    // Получаем значение из поля ввода
    var value = input.value;

    // Заменяем запятую на точку
    value = value.replace(',', '.');

    // Оставляем только цифры, точку и пробелы
    value = value.replace(/[^0-9.\s]/g, '');

    // Устанавливаем очищенное значение обратно в поле ввода
    input.value = value;
}