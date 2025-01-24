document.getElementById('weights').addEventListener('input', calculatePrice);
document.getElementsByName('payment_currency').forEach((radio) => {
    radio.addEventListener('change', calculatePrice);
});
