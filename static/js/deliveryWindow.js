// script.js
    // Обработчик для кнопки открытия модального окна "payment"
    document.getElementById("openDeliveryModal").addEventListener("click", function() {
        document.getElementById("DeliveryModal").style.display = "block";
    });

    // Обработчик для кнопки закрытия модального окна "payment"
    document.getElementById("closeDeliveryModal").addEventListener("click", function() {
        document.getElementById("DeliveryModal").style.display = "none";
    });

    // Обработчик для закрытия модального окна при клике вне окна
    window.addEventListener("click", function(event) {
        var modal = document.getElementById("DeliveryModal");
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Обработчик для закрытия модального окна при нажатии клавиши "Esc"
    window.addEventListener("keydown", function(event) {
        var modal = document.getElementById("DeliveryModal");
        if (event.key === "Escape" && modal.style.display === "block") {
            modal.style.display = "none";
        }
    });