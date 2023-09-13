// Скрыть все сообщения через 4 секунд
setTimeout(function() {
    var messages = document.querySelectorAll('.flash');
    for (var i = 0; i < messages.length; i++) {
        messages[i].style.display = 'none';
    }
}, 6000);








