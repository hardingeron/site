// Функция для открытия модального окна доставок
function openDeliveryModal() {
    document.getElementById("DeliveryModal").style.display = "block";
}

// Обработчик для кнопки закрытия модального окна "DeliveryModal"
document.getElementById("closeDeliveryModal").addEventListener("click", function() {
    document.getElementById("DeliveryModal").style.display = "none";
});

// Обработчик для закрытия модального окна при клике вне окна
window.addEventListener("click", function(event) {
    var deliveryModal = document.getElementById("DeliveryModal");
    
    if (event.target === deliveryModal) {
        deliveryModal.style.display = "none";
    }
});

// Обработчик для закрытия модального окна при нажатии клавиши "Esc"
window.addEventListener("keydown", function(event) {
    var deliveryModal = document.getElementById("DeliveryModal");
    
    if (event.key === "Escape" && deliveryModal.style.display === "block") {
        deliveryModal.style.display = "none";
    }
});

// Добавляем обработчики событий для кнопок доставок на грузинском языке
document.querySelectorAll('[data-lang="ge"]').forEach(function(element) {
    if (element.id === "openDeliveryModalGe") {
        element.addEventListener("click", openDeliveryModal);
    }
});

// Добавляем обработчики событий для кнопок доставок на русском языке
document.querySelectorAll('[data-lang="ru"]').forEach(function(element) {
    if (element.id === "openDeliveryModalRu") {
        element.addEventListener("click", openDeliveryModal);
    }
});
