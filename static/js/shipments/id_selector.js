document.addEventListener("DOMContentLoaded", () => {
    const exportBtn = document.getElementById("exportBtn");

    exportBtn.addEventListener("click", () => {
        const checked = document.querySelectorAll(
            'input[name="selected_shipments"]:checked'
        );

        // ❌ Ничего не выбрано
        if (checked.length === 0) {
            showToast("Выберите хотя бы одну посылку", "error");
            return;
        }

        const ids = Array.from(checked).map(cb => cb.value);

        fetch("/export_shipments", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ shipment_ids: ids }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error();
            }
            return response.json();
        })
        .then(data => {
            showToast("Данные успешно отправлены", "success");

            // ✅ очищаем чекбоксы
            checked.forEach(cb => cb.checked = false);
        })
        .catch(() => {
            showToast("Ошибка при выгрузке данных", "error");
        });
    });
});