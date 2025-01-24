function getWhereFrom() {
    // Примерная логика для получения значения из URL
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('where_from'); // Получаем значение параметра where_from из URL
}

function getSelectedCurrency() {
    const currencyRadios = document.getElementsByName('payment_currency');
    for (let radio of currencyRadios) {
        if (radio.checked) {
            return radio.value; // Возвращаем выбранную валюту
        }
    }
    return null; // Если ничего не выбрано, возвращаем null
}
