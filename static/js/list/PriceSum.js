function calculatePrice() {
    const weights = document.getElementById('weights').value.trim();
    const paymentField = document.getElementById('payment');
    const whereFrom = getWhereFrom(); // Функция, которая возвращает значение where_from (например, из URL)
    const currency = getSelectedCurrency(); // Функция для получения выбранной валюты

    // Разбираем веса (возможные пробелы между значениями)
    const weightList = weights.split(/\s+/).map(Number); // Разделяем по пробелам и превращаем в числа
    const totalWeight = weightList.reduce((acc, weight) => acc + weight, 0); // Суммируем веса

    let price = 0;

    // Проверяем, если вес меньше или равен 5 кг, используем фиксированную цену
    if (totalWeight <= 5) {  // Изменено условие на <= 5
        if (whereFrom === "Москва") {
            price = (currency === "GEL") ? 30 : 1000;
        } else if (whereFrom === "Санкт-Петербург") {
            price = (currency === "GEL") ? 40 : 1500;
        }
    } else {
        // Если вес больше 5 кг, используем динамическую цену в зависимости от валюты и места отправления
        if (currency === "GEL") {
            price = (whereFrom === "Москва") ? totalWeight * 6 : totalWeight * 8;
        } else if (currency === "RUB") {
            price = (whereFrom === "Москва") ? totalWeight * 200 : totalWeight * 250;
        }
    }

    // Округление до двух знаков после запятой
    price = parseFloat(price.toFixed(2));

    // Записываем цену в поле оплаты
    paymentField.value = price;
}
