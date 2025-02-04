document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("check").addEventListener("click", function (event) {
        event.preventDefault();  // Останавливаем отправку формы

        // Отключаем кнопку и меняем текст
        let button = document.getElementById("check");
        button.disabled = true;
        button.textContent = "!";

        let phone = document.getElementById("phone").value.trim();
        if (!phone) {
            alert("შეავსეთ ტელეფონის ველი!");
            // Восстанавливаем кнопку через 5 секунд
            setTimeout(function () {
                button.disabled = false;
                button.textContent = "?";
            }, 5000);
            return;
        }

        fetch("/check_user_with_phone", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ phone: phone })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector("[name='flname']").value = data.flname;
                document.querySelector("[name='pasport']").value = data.pasport;
                document.querySelector("[name='date_of_birth']").value = data.date_of_birth;

                if (data.gender === "male") {
                    document.getElementById("male").checked = true;
                } else if (data.gender === "female") {
                    document.getElementById("female").checked = true;
                }
            } else {
                alert("მონაცემები არ მოიძებნა!");
            }
        })
        .catch(error => console.error("Ошибка:", error))
        .finally(function () {
            // Восстанавливаем кнопку через 5 секунд, независимо от результата
            setTimeout(function () {
                button.disabled = false;
                button.textContent = "?";
            }, 5000);
        });
    });
});
