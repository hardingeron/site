// script.js
function sanitizeInput(input) {
    // Заменяем все нецифровые символы на пустую строку
    input.value = input.value.replace(/\D/g, '');
}