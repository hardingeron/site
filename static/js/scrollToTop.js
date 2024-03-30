// script.js
// Находим элемент фотографии
var scrollToTopButton = document.getElementById("scrollToTopButton");

// Добавляем обработчик события для клика
scrollToTopButton.addEventListener("click", function() {
    // Прокручиваем страницу наверх
    window.scrollTo({ top: 0, behavior: "smooth" });
});