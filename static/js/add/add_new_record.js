document.querySelector("form").addEventListener("submit", function(event) {
    event.preventDefault(); // Отменяем стандартное поведение формы

    // Сохраняем ссылку на кнопку
    const saveButton = document.querySelector("button[type='submit']");

    // Делаем кнопку неактивной и прозрачной
    saveButton.disabled = true;
    saveButton.style.opacity = '0.5';

    setTimeout(function() {
        saveButton.disabled = false;
        saveButton.style.opacity = '1';
    }, 2000);

    // Проверка каждого поля на заполнение
    const requiredFields = [
        { input: document.querySelector("input[name='sender']"), error: 'sender' },
        { input: document.querySelector("input[name='sender_phone']"), error: 'sender_phone' },
        { input: document.querySelector("input[name='recipient']"), error: 'recipient' },
        { input: document.querySelector("input[name='recipient_phone']"), error: 'recipient_phone' },
        { input: document.querySelector("textarea[name='inventory']"), error: 'inventory' },
        { input: document.querySelector("input[name='weight']"), error: 'weight' },
        { input: document.querySelector("input[name='cost']"), error: 'cost' },
        { input: document.querySelector("select[name='city']"), error: 'city' },
        { input: document.querySelector("input[name='payment']:checked"), error: 'payment' },
        { input: document.querySelector("input[name='payment_currency']:checked"), error: 'payment_currency' }
    ];

    let isValid = true;

    for (const { input, error } of requiredFields) {
        const value = input ? input.value.trim() : "";

        if (value === "") {
            isValid = false;
            if (input) {
                input.style.border = '1px solid red';
                setTimeout(() => {
                    input.style.border = '1px solid #9c9c9c7a';
                }, 2000);
            }
        }
    }

    if (!isValid) {
        Swal.fire({
            icon: 'error',
            title: 'შეცდომა!',
            text: 'შეავსეთ მითითებული ველები!'
        });
        return;
    }

    // Соберите данные из всех инпутов и радио-кнопок
    var formData = new FormData();

    // Добавьте значения инпутов
    formData.append("sender", document.querySelector("input[name='sender']").value);
    formData.append("sender_phone", document.querySelector("input[name='sender_phone']").value);
    formData.append("recipient", document.querySelector("input[name='recipient']").value);
    formData.append("recipient_phone", document.querySelector("input[name='recipient_phone']").value);
    formData.append("inventory", document.querySelector("textarea[name='inventory']").value);
    formData.append("weight", document.querySelector("input[name='weight']").value);
    formData.append("responsibility", document.querySelector("input[name='responsibility']").value);
    formData.append("passport", document.querySelector("input[name='passport']").value);
    formData.append("cost", document.querySelector("input[name='cost']").value);
    formData.append("city", document.querySelector("select[name='city']").value);

    // Добавьте значения радио-кнопок
    const paymentMethod = document.querySelector("input[name='payment']:checked");
    if (paymentMethod) {
        formData.append("payment", paymentMethod.value);
    }
    const paymentCurrency = document.querySelector("input[name='payment_currency']:checked");
    if (paymentCurrency) {
        formData.append("payment_currency", paymentCurrency.value);
    }

    // Добавьте файл
    var photoInput = document.getElementById("photo");
    var photoFile = photoInput.files[0];
    if (photoFile) {
        formData.append("photo", photoFile);
    }

    // Получите текущую дату и время
    var currentDate = new Date();

    // получение информации о статусе отправки
    var departureStatus = document.getElementById("departureStatus").checked;
    formData.append("departureStatus", departureStatus ? "selected" : "not selected");

    // Функция для добавления ведущего нуля к числам, если они меньше 10
    function addLeadingZero(number) {
        return number < 10 ? "0" + number : number;
    }

    // Форматирование даты в нужный формат (д.м.г.ч.м.с)
    var formattedDate = addLeadingZero(currentDate.getDate()) + '.' +
                        addLeadingZero(currentDate.getMonth() + 1) + '.' +
                        currentDate.getFullYear() + ' ' +
                        addLeadingZero(currentDate.getHours()) + ':' +
                        addLeadingZero(currentDate.getMinutes()) + ':' +
                        addLeadingZero(currentDate.getSeconds());

    // Добавьте отформатированную дату и время в объект FormData
    formData.append("currentDateTime", formattedDate);

    // Отправьте данные на сервер
    fetch("/saving_a_parcel", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                icon: 'success',
                title: 'წარმატება!',
                text: data.message,
                showConfirmButton: false,
                timer: 5000
            });
            // Очистка полей, радиокнопок и загруженного файла
            document.querySelector("input[name='sender']").value = '';
            document.querySelector("input[name='sender_phone']").value = '';
            document.querySelector("input[name='recipient']").value = '';
            document.querySelector("input[name='recipient_phone']").value = '';
            document.querySelector("textarea[name='inventory']").value = '';
            document.querySelector("input[name='weight']").value = '';
            document.querySelector("input[name='responsibility']").value = '';
            document.querySelector("input[name='passport']").value = '';
            document.querySelector("input[name='cost']").value = '';
            document.querySelector("select[name='city']").value = '';
            document.querySelector("input[name='payment']:checked").checked = false;
            document.querySelector("input[name='payment_currency']:checked").checked = false;
            document.getElementById("photo").value = ''; // Очистка загруженного файла
            document.getElementById("departureStatus").checked = false;

        } else {
            Swal.fire({
                icon: 'error',
                title: 'შეცდომა!',
                text: data.message
            });
        }
    })
    .catch(error => {
        console.error("Ошибка при отправке запроса:", error);
    });
});