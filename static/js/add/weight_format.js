function formatWeight(input) {
    let value = input.value;
    
    // Заменяем запятые на точки
    value = value.replace(/,/g, '.');

    // Удаляем все символы, кроме цифр и точек
    value = value.replace(/[^\d.]/g, '');

    // Ограничиваем максимальную длину в 10 символов
    value = value.substring(0, 10);

    // Устанавливаем отформатированное значение обратно в инпут
    input.value = value;
}