function formatPhoneNumber(input) {
    // Получаем текущее значение
    let value = input.value;

    // Удаляем все символы, кроме цифр
    value = value.replace(/\D/g, '');

    // Ограничиваем максимальную длину в 9 символов
    value = value.substring(0, 9);

    // Устанавливаем отформатированное значение обратно в инпут
    input.value = value;

    // Проверяем, если количество символов меньше 9, окрашиваем границы в красный
    if (value.length < 9) {
        input.style.border = '1px solid red';
    } else {
        input.style.border = '1px solid #ccc'; // возвращаем обычный цвет границы
    }
}

document.getElementById("sender_phone").addEventListener("input", function() {
    // Получаем текущее значение
    let value = this.value;

    // Удаляем все символы, кроме цифр
    value = value.replace(/\D/g, '');

    // Ограничиваем максимальную длину в 9 символов
    value = value.substring(0, 9);

    // Устанавливаем отформатированное значение обратно в инпут
    this.value = value;

    // Проверяем, если количество символов меньше 9, окрашиваем границы в красный
    if (value.length < 9) {
        this.style.border = '1px solid red';
    } else {
        this.style.border = '1px solid #ccc'; // возвращаем обычный цвет границы
    }
});