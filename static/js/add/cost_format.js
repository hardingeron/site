function formatCost(input) {
    let value = input.value;
    
    // Удаляем все символы, кроме цифр
    value = value.replace(/\D/g, '');

    // Устанавливаем отформатированное значение обратно в инпут
    input.value = value;
}