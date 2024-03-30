// script.js
    // Обработчик для кнопки открытия модального окна "payment"
    document.getElementById("openPaymentModal").addEventListener("click", function() {
        document.getElementById("PaymentModal").style.display = "block";
    });

    // Обработчик для кнопки закрытия модального окна "payment"
    document.getElementById("closePaymentModal").addEventListener("click", function() {
        document.getElementById("PaymentModal").style.display = "none";
    });

    // Обработчик для закрытия модального окна при клике вне окна
    window.addEventListener("click", function(event) {
        var modal = document.getElementById("PaymentModal");
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Обработчик для закрытия модального окна при нажатии клавиши "Esc"
    window.addEventListener("keydown", function(event) {
        var modal = document.getElementById("PaymentModal");
        if (event.key === "Escape" && modal.style.display === "block") {
            modal.style.display = "none";
        }
    });