// Функция для открытия модального окна статистики
function openStatsModal() {
    document.getElementById("PaymentModal").style.display = "block";
}

// Обработчик для кнопки закрытия модального окна "PaymentModal"
document.getElementById("closePaymentModal").addEventListener("click", function() {
    document.getElementById("PaymentModal").style.display = "none";
});

// Обработчик для закрытия модального окна при клике вне окна
window.addEventListener("click", function(event) {
    var paymentModal = document.getElementById("PaymentModal");
    
    if (event.target === paymentModal) {
        paymentModal.style.display = "none";
    }
});

// Обработчик для закрытия модального окна при нажатии клавиши "Esc"
window.addEventListener("keydown", function(event) {
    var paymentModal = document.getElementById("PaymentModal");
    
    if (event.key === "Escape" && paymentModal.style.display === "block") {
        paymentModal.style.display = "none";
    }
});

// Добавляем обработчики событий для кнопок статистики на грузинском языке
document.querySelectorAll('[data-lang="ge"]').forEach(function(element) {
    if (element.id === "openPaymentModalGe") {
        element.addEventListener("click", openStatsModal);
    }
});

// Добавляем обработчики событий для кнопок статистики на русском языке
document.querySelectorAll('[data-lang="ru"]').forEach(function(element) {
    if (element.id === "openPaymentModalRu") {
        element.addEventListener("click", openStatsModal);
    }
});
