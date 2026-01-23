// Валидация ввода телефона в формате +7XXXXXXXXXX
const phoneInput = document.getElementById("senderPhone");

phoneInput.addEventListener("focus", () => {
    if (!phoneInput.value) {
        phoneInput.value = "+7";
    }
});

phoneInput.addEventListener("input", () => {
    let value = phoneInput.value;

    // всегда начинаем с +7
    if (!value.startsWith("+7")) {
        value = "+7";
    }

    // берём всё после +7 и оставляем только цифры
    let digits = value.slice(2).replace(/\D/g, "");

    // ограничиваем 10 цифрами
    digits = digits.slice(0, 10);

    phoneInput.value = "+7" + digits;
});

// защита от удаления +7
phoneInput.addEventListener("keydown", (e) => {
    if (
        (e.key === "Backspace" || e.key === "Delete") &&
        phoneInput.selectionStart <= 2
    ) {
        e.preventDefault();
    }
});





// Валидация ввода телефона в формате 5XXXXXXXXX
const recipientPhoneInput = document.getElementById("recipientPhone");

recipientPhoneInput.addEventListener("focus", () => {
    if (!recipientPhoneInput.value) {
        recipientPhoneInput.value = "5";
    }
});

recipientPhoneInput.addEventListener("input", () => {
    let value = recipientPhoneInput.value;

    // всегда начинаем с 5
    if (!value.startsWith("5")) {
        value = "5";
    }

    // всё после первой 5 — только цифры
    let digits = value.slice(1).replace(/\D/g, "");

    // максимум 8 цифр после 5
    digits = digits.slice(0, 8);

    recipientPhoneInput.value = "5" + digits;
});

// защита от удаления первой 5
recipientPhoneInput.addEventListener("keydown", (e) => {
    if (
        (e.key === "Backspace" || e.key === "Delete") &&
        recipientPhoneInput.selectionStart <= 1
    ) {
        e.preventDefault();
    }
});
