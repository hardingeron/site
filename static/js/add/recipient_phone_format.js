function formatRecipientPhone(input) {
    let value = input.value;
    
    // Удаляем все символы, кроме "+" и цифр
    value = value.replace(/[^\+\d]/g, '');

    // Если символ "+" не первый, удаляем его
    if (value.indexOf('+') !== 0) {
        value = value.replace('+', '');
    }

    // Ограничиваем максимальную длину в 12 символов (включая символ "+")
    value = value.substring(0, 12);

    // Устанавливаем очищенное значение обратно в инпут
    input.value = value;

    // Проверяем, если количество символов меньше 12, окрашиваем границы в красный
    if (value.length < 12) {
        input.style.border = '1px solid red';
    } else {
        input.style.border = '1px solid #ccc'; // возвращаем обычный цвет границы
    }
}