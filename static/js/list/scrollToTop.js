// script.js
document.addEventListener("DOMContentLoaded", function() {
    var scrollToTopButton = document.getElementById("scrollToTopButton");

    // Скрываем кнопку при загрузке страницы
    scrollToTopButton.style.display = "none";

    // Добавляем обработчик события для прокрутки
    window.addEventListener("scroll", function() {
        // Если пользователь прокрутил страницу вниз, показываем кнопку, иначе скрываем
        if (window.scrollY > 100) {
            scrollToTopButton.style.display = "block";
        } else {
            scrollToTopButton.style.display = "none";
        }
    });

    // Добавляем обработчик события для клика
    scrollToTopButton.addEventListener("click", function() {
        // Прокручиваем страницу наверх
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
});