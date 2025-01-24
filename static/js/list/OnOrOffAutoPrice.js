function togglePaymentField() {
    const paymentField = document.getElementById('payment');
    const enablePaymentButton = document.getElementById('enable_payment_button');
    
    // Проверяем, был ли клик по кнопке (когда кнопка активна)
    if (paymentField.readOnly) {
        paymentField.readOnly = false;
        paymentField.value = ''; // Очищаем поле, если включили редактирование
        enablePaymentButton.classList.remove('btn-primary');  // Убираем синий цвет
        enablePaymentButton.classList.add('btn-success');  // Кнопка становится зеленой
        enablePaymentButton.textContent = 'არასტანდარტული'; // Меняем текст на "არასტანდარტული"
    } else {
        paymentField.readOnly = true;
        paymentField.value = ''; // Очищаем поле, если выключили редактирование
        enablePaymentButton.classList.remove('btn-success');  // Убираем зеленый цвет
        enablePaymentButton.classList.add('btn-primary');  // Кнопка возвращается в синий
        enablePaymentButton.textContent = 'სტანდარტული'; // Меняем текст на "სტანდარტული"
    }
}
