document.addEventListener("DOMContentLoaded", () => {
    const issueButtons = document.querySelectorAll(".issue-btn");
    const issueModalEl = document.getElementById("issueModal");
    const issueModal = new bootstrap.Modal(issueModalEl);

    const recipientInfoEl = document.getElementById("recipient-info");
    const foundParcelsEl = document.getElementById("found-parcels");
    const parcelListEl = document.getElementById("parcel-list");
    const passportInputEl = document.getElementById("passport-input");
    const passportCounterEl = document.getElementById("passport-counter");
    const submitBtn = document.getElementById("issue-submit-btn");
    const residentCheckboxEl = document.getElementById("resident-checkbox");
    const warningEl = document.getElementById("warning-message");

    let currentShipmentId = null;
    let currentParcels = [];

    // =========================
    // 🔢 СЧЁТЧИК СИМВОЛОВ
    // =========================
    passportInputEl.addEventListener("input", () => {
        let value = passportInputEl.value;
        const isResident = residentCheckboxEl.checked;

        // 🔒 Ограничение длины
        if (isResident && value.length > 11) {
            value = value.slice(0, 11);
            passportInputEl.value = value;
        } else if (!isResident && value.length > 121) {
            value = value.slice(0, 121);
            passportInputEl.value = value;
        }

        const length = value.length;

        // Обновляем счетчик
        passportCounterEl.textContent = `${length} символов`;

        // Сброс цветов
        passportCounterEl.classList.remove("text-success", "text-primary", "text-danger", "text-muted");

        // Подсветка по условиям
        if (isResident && length !== 11) {
            passportCounterEl.classList.add("text-danger");
        } else if (!isResident && length < 4) {
            passportCounterEl.classList.add("text-danger");
        } else if (length === 9) {
            passportCounterEl.classList.add("text-success");
        } else if (length === 11) {
            passportCounterEl.classList.add("text-primary");
        } else {
            passportCounterEl.classList.add("text-muted");
        }
    });

    // =========================
    // 📦 КНОПКА "ВЫДАТЬ"
    // =========================
    issueButtons.forEach(btn => {
        btn.addEventListener("click", async () => {
            currentShipmentId = btn.dataset.id;

            try {
                const response = await fetch(`/get_shipment/${currentShipmentId}`);
                if (!response.ok) throw new Error("Ошибка загрузки данных");

                const data = await response.json();
                const recipientName = data.recipient_name + " " + data.recipient_surname;
                currentParcels = data.parcels;

    
                // ⚠️ Предупреждение
                if (data.warning) {
                    warningEl.textContent = data.warning;
                    warningEl.classList.remove("d-none");
                } else {
                    warningEl.classList.add("d-none");
                    warningEl.textContent = "";
                }

                // Обновляем UI получателя
                recipientInfoEl.textContent = recipientName;
                foundParcelsEl.textContent = `Найдено посылок: ${currentParcels.length}`;

                // Список посылок
                parcelListEl.innerHTML = "";
                currentParcels.forEach(p => {
                    const card = document.createElement("div");
                    card.className = "card shadow-sm mb-2 rounded-3";

                    const borderColor = data.warning ? "border-danger" : "border-primary";

                    card.innerHTML = `
                        <div class="card-body p-2 d-flex justify-content-between align-items-center border-start border-4 ${borderColor}">
                            <span class="fw-semibold">${p.number}</span>
                            <span class="badge bg-light text-dark fw-semibold">${p.weight} kg</span>
                        </div>
                    `;
                    parcelListEl.appendChild(card);
                });

                // Автоподстановка паспорта
                passportInputEl.value = data.recipient_passport || "";
                passportInputEl.dispatchEvent(new Event("input"));

                // Сброс чекбокса
                residentCheckboxEl.checked = false;

                // 🔹 Важно! Модальное окно показываем даже если нет посылок, чтобы видно было предупреждение
                issueModal.show();

            } catch (err) {
                console.error(err);
                alert("Не удалось загрузить данные посылки.");
            }
        });
    });

    // =========================
    // 🚀 ОТПРАВКА
    // =========================
    submitBtn.addEventListener("click", async () => {
        const passport = passportInputEl.value.trim();
        const resident = residentCheckboxEl.checked ? 1 : 0;

        // ❗ проверка
        if (resident && passport.length !== 11) {
            alert("Для резидента страны паспорт должен содержать ровно 11 символов!");
            return;
        } else if (!resident && passport.length < 4) {
            alert("Паспорт должен содержать минимум 4 символа!");
            return;
        }

        // ❗ подтверждение
        const confirmAction = confirm(
            `Проверь данные:\n\nПаспорт: ${passport}\nРезидент: ${resident ? "Да" : "Нет"}\nПосылок: ${currentParcels.length}\n\nВыдать?`
        );

        if (!confirmAction) return;

        const payload = {
            shipment_id: currentShipmentId,
            parcels: currentParcels.map(p => p.number),
            passport: passport,
            resident: resident
        };

        try {
            submitBtn.disabled = true;
            submitBtn.textContent = "Отправка...";

            const response = await fetch("/issue_shipment", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                alert("Посылки успешно выданы!");
                const card = document.querySelector(`[data-shipment-id="${currentShipmentId}"]`);
                if (card) card.classList.add("issued");
                issueModal.hide();
            } else {
                alert("Ошибка: " + result.message);
            }

        } catch (err) {
            console.error(err);
            alert("Не удалось отправить данные.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Выдать посылки";
        }
    });

    // =========================
    // 🔄 обновляем счетчик при смене чекбокса
    // =========================
    residentCheckboxEl.addEventListener("change", () => passportInputEl.dispatchEvent(new Event("input")));
});
