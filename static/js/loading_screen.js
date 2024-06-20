function animateSpinners() {
    var spinners = document.querySelectorAll(".loading-spinner");
    
    function animate(index) {
        if (index >= spinners.length) {
            // Все кружочки исчезли, скрываем фон загрузки
            var loadingScreen = document.getElementById("loading-screen");
            loadingScreen.style.opacity = "0";
            setTimeout(function () {
                loadingScreen.style.display = "none";
            }, 500); // После 500 миллисекунд (0.5 секунды) скрыть фон
            return;
        }
        
        // Плавно скрываем текущий кружок
        spinners[index].style.opacity = "0";
        setTimeout(function () {
            // Затем анимируем следующий кружок
            animate(index + 1);
        }, 600); // После 600 миллисекунд (0.6 секунды) анимировать следующий
    }
    
    // Показать контент перед анимацией спинеров
    document.getElementById('page-content').style.display = 'block';
    animate(0); // Начнем с первого кружка
}

// Вызываем функцию анимации после загрузки страницы
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(animateSpinners, 100); // Запустить анимацию через 100 миллисекунд после загрузки
});