// ----- валидация отправителя и получяателя как имени так ияяяян -----
  // IDs всех полей, к которым нужно применить валидацию
  const nameFieldIds = [
    "sender_first_name",
    "sender_last_name",
    "recipient_first_name",
    "recipient_last_name"
  ];

  // Функция, применяющая логику валидации к одному полю
  function applyNameValidation(input) {
    // Во время ввода
    input.addEventListener("input", function () {
      let v = input.value.toUpperCase();
      v = v.replace(/[^A-Z-]/g, "");    // Только A-Z и тире
      v = v.replace(/--+/g, "-");       // Одинарное тире
      v = v.replace(/^-+/, "");         // Удалить ведущие тире
      if (v.length > 50) v = v.slice(0, 50); // Ограничение по длине
      input.value = v;
    });

    // При потере фокуса — удалить конечные тире
    input.addEventListener("blur", function () {
      input.value = input.value.replace(/-+$/, "");
    });

    // Вставка — чистим всё, кроме допустимого
    input.addEventListener("paste", function (e) {
      e.preventDefault();
      const text = (e.clipboardData || window.clipboardData).getData("text");
      let v = text.toUpperCase().replace(/[^A-Z-]/g, "");
      v = v.replace(/--+/g, "-");
      v = v.replace(/^-+/, "").slice(0, 50);
      input.value = v;
    });

    // Запретить ввод любых недопустимых символов
    input.addEventListener("keypress", function (e) {
      const ch = String.fromCharCode(e.which).toUpperCase();
      if (!/^[A-Z-]$/.test(ch)) {
        e.preventDefault();
      }
    });
  }

  // Применяем функцию ко всем полям
  nameFieldIds.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      applyNameValidation(input);
    }
  });


// ----- валидация номера отправителя -----
  const senderPhoneInput = document.getElementById("sender_phone");

  // Функция установки и контроля формата
  function formatsenderPhoneInput() {
    let value = senderPhoneInput.value;

    // Удаляем всё, кроме цифр
    value = value.replace(/\D/g, "");

    // Убираем первую 7 или 8, если пользователь её ввёл — она уже есть как +7
    if (value.startsWith("7") || value.startsWith("8")) {
      value = value.slice(1);
    }

    // Обрезаем до 10 цифр
    value = value.slice(0, 10);

    // Устанавливаем в поле значение в виде +7XXXXXXXXXX
    senderPhoneInput.value = "+7" + value;
  }

  // При фокусе — если поле пустое, устанавливаем +7
  senderPhoneInput.addEventListener("focus", function () {
    if (!senderPhoneInput.value.startsWith("+7")) {
      senderPhoneInput.value = "+7";
    }
  });

  // Обработка ввода
  senderPhoneInput.addEventListener("input", function () {
    formatsenderPhoneInput();
  });

  // Блокировка удаления +7
  senderPhoneInput.addEventListener("keydown", function (e) {
    const pos = senderPhoneInput.selectionStart;

    // Блокируем удаление символов до индекса 2 (то есть `+7`)
    if ((e.key === "Backspace" && pos <= 2) ||
        (e.key === "Delete" && pos < 3)) {
      e.preventDefault();
    }

    // Блокируем ввод, если уже 12 символов
    if (senderPhoneInput.value.length >= 12 && 
        !["Backspace", "Delete", "ArrowLeft", "ArrowRight"].includes(e.key) &&
        senderPhoneInput.selectionStart >= 12) {
      e.preventDefault();
    }
  });

  // Блокировка вставки "мусора"
  senderPhoneInput.addEventListener("paste", function (e) {
    e.preventDefault();
    const text = (e.clipboardData || window.clipboardData).getData("text");
    const digits = text.replace(/\D/g, "").slice(0, 10);
    senderPhoneInput.value = "+7" + digits;
  });



// ----- валидатор номера получателя -----
document.addEventListener("DOMContentLoaded", () => {
    const phoneInput = document.getElementById("recipient_phone");
    if (!phoneInput) return;
  
    const PREFIX = "+995";
  
    // При фокусе — всегда ставим курсор в конец
    phoneInput.addEventListener("focus", () => {
      // Ждем, пока браузер поставит фокус
      setTimeout(() => {
        const len = phoneInput.value.length;
        phoneInput.setSelectionRange(len, len);
      }, 0);
      // Если поле пустое, сразу префикс
      if (!phoneInput.value.startsWith(PREFIX)) {
        phoneInput.value = PREFIX;
      }
    });
  
    // Блокировка удаления префикса
    phoneInput.addEventListener("keydown", (e) => {
      const pos = phoneInput.selectionStart;
      // Блокируем Backspace, если курсор в пределах префикса
      if (e.key === "Backspace" && pos <= PREFIX.length) {
        e.preventDefault();
      }
      // Блокируем Delete, если курсор строго перед префиксом
      if (e.key === "Delete" && pos < PREFIX.length) {
        e.preventDefault();
      }
    });
  
    // При любом вводе — оставляем только цифры после префикса и обрезаем до 9 цифр
    phoneInput.addEventListener("input", () => {
      let digits = phoneInput.value
        .slice(PREFIX.length)      // берём всё после "+995"
        .replace(/\D/g, "")        // убираем не‑цифры
        .slice(0, 9);              // максимум 9 цифр
  
      phoneInput.value = PREFIX + digits;
    });
  
    // Вставка — точно так же
    phoneInput.addEventListener("paste", (e) => {
      e.preventDefault();
      const pasted = (e.clipboardData || window.clipboardData)
        .getData("text")
        .replace(/\D/g, "")
        .slice(0, 9);
      phoneInput.value = PREFIX + pasted;
    });
  });



  // Массив id паспортных полей
  const passportIds = ["sender_passport", "recipient_passport"];

  passportIds.forEach(id => {
    const input = document.getElementById(id);

    // Ввод
    input.addEventListener("input", function () {
      let v = input.value.toUpperCase();
      v = v.replace(/[^A-Z0-9]/g, ""); // Убираем всё кроме латиницы и цифр
      if (v.length > 30) v = v.slice(0, 30);
      input.value = v;
    });

    // Вставка
    input.addEventListener("paste", function (e) {
      e.preventDefault();
      const text = (e.clipboardData || window.clipboardData).getData("text");
      let v = text.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 30);
      input.value = v;
    });

    // Блокируем недопустимые клавиши
    input.addEventListener("keypress", function (e) {
      const ch = String.fromCharCode(e.which).toUpperCase();
      if (!/^[A-Z0-9]$/.test(ch)) {
        e.preventDefault();
      }
    });
  });
