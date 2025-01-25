function calculatePrice() {
    const enablePaymentButton = document.getElementById('enable_payment_button');

    // Проверяем, находится ли кнопка в состоянии "არასტანდარტული"
    if (enablePaymentButton.textContent.trim() === 'არასტანდარტული') {
        return; // Если да, не производим пересчет
    }

    const weights = document.getElementById('weights').value.trim();
    const paymentField = document.getElementById('payment');
    const whereFrom = getWhereFrom(); // Функция, которая возвращает значение where_from (например, из URL)
    const currency = getSelectedCurrency(); // Функция для получения выбранной валюты

    // Разбираем веса (возможные пробелы между значениями)
    const weightList = weights.split(/\s+/).map(Number); // Разделяем по пробелам и превращаем в числа
    const totalWeight = weightList.reduce((acc, weight) => acc + weight, 0); // Суммируем веса

    let price = 0;

    // Проверяем, если вес меньше или равен 5 кг, используем фиксированную цену
    if (totalWeight <= 5) {
        if (whereFrom === "Москва") {
            price = (currency === "GEL") ? 30 : 1000;
        } else if (whereFrom === "Санкт-Петербург") {
            price = (currency === "GEL") ? 50 : 1500;
        }
    } else {
        // Если вес больше 5 кг, используем динамическую цену в зависимости от валюты и места отправления
        if (currency === "GEL") {
            price = (whereFrom === "Москва") ? totalWeight * 6 : totalWeight * 8;
        } else if (currency === "RUB") {
            price = (whereFrom === "Москва") ? totalWeight * 200 : totalWeight * 250;
        }
    }

    // Округляем вверх до целого числа
    price = Math.ceil(price);

    // Записываем цену в поле оплаты
    paymentField.value = price;
}

// Обновляем слушатели
document.getElementById('weights').addEventListener('input', calculatePrice);
document.getElementsByName('payment_currency').forEach((radio) => {
    radio.addEventListener('change', calculatePrice);
});
