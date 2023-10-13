    // Функция для анимации кружочков
    function animateSpinners() {
        var spinners = document.querySelectorAll(".loading-spinner");
        
        function animate(index) {
            if (index >= spinners.length) {
                // Все кружочки исчезли, скрываем фон загрузки
                var loadingScreen = document.getElementById("loading-screen");
                loadingScreen.style.opacity = "0";
                setTimeout(function () {
                    loadingScreen.style.display = "none";
                    
                    // Показываем остальной контент страницы
                    var pageContent = document.getElementById('page-content');
                    pageContent.style.display = 'block';
                }, 100); // После 200 миллисекунд (0.2 секунды) скрыть фон
                return;
            }
            
            // Плавно скрываем текущий кружок
            spinners[index].style.opacity = "0";
            setTimeout(function () {
                // Затем анимируем следующий кружок
                animate(index + 1);
            }, 300); // После 200 миллисекунд (0.2 секунды) анимировать следующий
        }
        
        animate(0); // Начнем с первого кружка
    }
    
    // Вызываем функцию анимации после загрузки страницы
    document.addEventListener("DOMContentLoaded", function () {
        setTimeout(animateSpinners, 10); // Запустить анимацию через 10 миллисекунд после загрузки
    });