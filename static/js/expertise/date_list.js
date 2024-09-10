document.getElementById('toggleDateList').addEventListener('click', function() {
    const dateList = document.getElementById('dateList');
        
    // Если список открыт, мы его закроем
    if (dateList.classList.contains('show')) {
        dateList.style.maxHeight = null;
        dateList.classList.remove('show');
    } 
    // Если список закрыт, мы его откроем
    else {
        dateList.style.maxHeight = dateList.scrollHeight + "px"; // Автоматическое вычисление высоты
        dateList.classList.add('show');
    }
});
