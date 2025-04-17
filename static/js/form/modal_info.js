
// Скрипт для автоматического открытия модального окна
window.onload = function() {
    var modal = new bootstrap.Modal(document.getElementById('infoModal'), {
    keyboard: false,  // Окно нельзя закрыть с помощью клавиши ESC
    backdrop: 'static' // Окно не закрывается при клике вне окна
    });
    modal.show(); // Окно появляется сразу при загрузке страницы
};

// Скрыть окно при нажатии "Подтвердить"
document.getElementById('confirmBtn').addEventListener('click', function() {
    var modal = bootstrap.Modal.getInstance(document.getElementById('infoModal'));
    modal.hide(); // Скрыть окно сразу после подтверждения
});
