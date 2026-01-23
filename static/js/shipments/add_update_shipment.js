
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("parcelModal");
    const closeBtn = document.getElementById("closeModalBtn");
    const finishBtn = document.getElementById("finishBtn");

    const inputWeight = document.getElementById("parcelWeight");
    const weightContainer = document.getElementById("weightContainer");
    const hiddenWeightInput = document.getElementById("weightsHidden");

    const inputInventory = document.getElementById("inventoryInput");
    const inventoryContainer = document.getElementById("inventoryContainer");

    // -------------------------------
    // Теги весов
    // -------------------------------
    function formatWeight(value) {
        let num = parseFloat(value);
        if (isNaN(num)) return "0.00";
        return num.toFixed(2);
    }

    function updateHiddenWeights() {
        const weights = [];
        weightContainer.querySelectorAll(".weight-tag").forEach(tag => {
            weights.push(tag.textContent);
        });
        hiddenWeightInput.value = weights.join(" ");
    }

    function addWeightTag(value) {
        const formattedValue = formatWeight(value);
        const tag = document.createElement("div");
        tag.classList.add("weight-tag");
        tag.textContent = formattedValue;
        weightContainer.appendChild(tag);
        updateHiddenWeights();
    }

    function initWeightTags(weightsString) {
        weightContainer.innerHTML = "";
        if (!weightsString) return;
        const weightsArray = weightsString.split(/\s+/);
        weightsArray.forEach(w => addWeightTag(w));
    }

    // -------------------------------
    // Теги описания
    // -------------------------------
    function addInventoryTag(text) {
        if (!text.trim()) return;
        const tag = document.createElement("div");
        tag.classList.add("inventory-tag");

        const span = document.createElement("span");
        span.textContent = text.trim();

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => inventoryContainer.removeChild(tag));

        tag.appendChild(span);
        tag.appendChild(removeBtn);
        inventoryContainer.appendChild(tag);
    }

    function initInventoryTags(descriptionString) {
        inventoryContainer.innerHTML = "";
        if (!descriptionString) return;
        const items = descriptionString.split(",").map(s => s.trim()).filter(s => s);
        items.forEach(item => addInventoryTag(item));
    }

    // -------------------------------
    // Закрытие модалки
    // -------------------------------
    function closeModal() {
        modal.style.display = "none";
        resetModalFields();
        goToStep(0);
        delete modal.dataset.editId;
    }

    closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
    });

    // -------------------------------
    // Новая посылка
    // -------------------------------
    const addCard = document.getElementById("addParcelCard");
    addCard.addEventListener("click", () => {
        modal.style.display = "flex";
        delete modal.dataset.editId;
        resetModalFields();
        goToStep(0);
    });

    // -------------------------------
    // Редактирование существующей посылки
    // -------------------------------
    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const shipmentId = btn.dataset.id;
            const response = await fetch(`/shipments/${shipmentId}`);
            if (!response.ok) return alert("Ошибка при загрузке данных");
            const data = await response.json();

            // безопасное присваивание значений
            function safeSetValue(id, value) {
                const el = document.getElementById(id);
                if (el) el.value = value || "";
            }

            safeSetValue("senderName", data.sender_name);
            safeSetValue("senderSurname", data.sender_surname);
            safeSetValue("senderPhone", data.sender_number);

            safeSetValue("recipientName", data.recipient_name);
            safeSetValue("recipientSurname", data.recipient_surname);
            safeSetValue("recipientPhone", data.recipient_number);
            safeSetValue("recipientPassport", data.recipient_passport);

            safeSetValue("parcelCity", data.city_to);
            safeSetValue("parcelCost", data.cargo_cost);
            safeSetValue("parcelAddress", data.address);
            safeSetValue("paymentAmount", data.payment_amount);

            // ---- теги весов ----
            inputWeight.value = "";
            hiddenWeightInput.value = data.weights || "";
            initWeightTags(data.weights);

            // ---- теги описания ----
            inputInventory.value = "";
            initInventoryTags(data.description || "");

            // ---- radio кнопки ----
            document.querySelectorAll('input[name="payment"]').forEach(r => r.checked = false);
            if (data.payment_status) {
                const payEl = document.getElementById(data.payment_status);
                if (payEl) payEl.checked = true;
            }

            document.querySelectorAll('input[name="currency"]').forEach(r => r.checked = false);
            if (data.currency) {
                const curEl = document.getElementById(data.currency);
                if (curEl) curEl.checked = true;
            }

            modal.dataset.editId = shipmentId;
            modal.style.display = "flex";
            goToStep(0);
        });
    });

    // -------------------------------
    // Отправка формы
    // -------------------------------
    finishBtn.addEventListener("click", async () => {
        const sharedRecipient = document.getElementById("sharedRecipient").checked;
        let step4Valid = true;

        if (!sharedRecipient) {
            const amount = document.getElementById("paymentAmount");
            const payment = document.querySelector('input[name="payment"]:checked');
            const currency = document.querySelector('input[name="currency"]:checked');

            if (!amount.value.trim()) {
                amount.classList.add('placeholder-error');
                setTimeout(() => amount.classList.remove('placeholder-error'), 2000);
                step4Valid = false;
            }
            if (!payment) step4Valid = false;
            if (!currency) step4Valid = false;
        }

        if (!step4Valid) return;

        const urlParams = new URLSearchParams(window.location.search);
        const dateParam = urlParams.get("date") || "";
        const whereFromParam = urlParams.get("where_from") || "";

        const payload = {
            shipmentId: modal.dataset.editId || null,
            senderName: document.getElementById("senderName").value,
            senderSurname: document.getElementById("senderSurname").value,
            senderPhone: document.getElementById("senderPhone").value,

            recipientName: document.getElementById("recipientName").value,
            recipientSurname: document.getElementById("recipientSurname").value,
            recipientPhone: document.getElementById("recipientPhone").value,
            recipientPassport: document.getElementById("recipientPassport").value,

            weightsHidden: hiddenWeightInput.value,
            parcelCity: document.getElementById("parcelCity").value,
            parcelCost: document.getElementById("parcelCost").value,
            parcelAddress: document.getElementById("parcelAddress").value,

            inventory: Array.from(inventoryContainer.children)
                            .map(e => e.textContent.trim()),

            paymentAmount: document.getElementById("paymentAmount").value,
            paymentStatus: document.querySelector('input[name="payment"]:checked')?.id || "",
            currency: document.querySelector('input[name="currency"]:checked')?.id || "",
            sharedRecipient: sharedRecipient,

            date: dateParam,
            where_from: whereFromParam
        };

        try {
            const res = await fetch("/shipment_submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await res.json();
            if (res.ok && result.success) {
                alert(result.message);
                closeModal();
                location.reload();
            } else {
                alert("Ошибка при сохранении: " + (result.message || "неизвестная"));
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка при сохранении");
        }
    });
});
