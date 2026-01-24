document.addEventListener("DOMContentLoaded", () => {
    const exportBtn = document.getElementById("downloadExcelBtn");
    const selectAll = document.getElementById("selectAllShipments");

    if (!exportBtn) {
        console.error("Кнопка downloadExcelBtn не найдена");
        return;
    }

    exportBtn.addEventListener("click", () => {
        const checked = Array.from(
            document.querySelectorAll('input[name="selected_shipments"]:checked')
        );

        if (checked.length === 0) {
            showToast("Выберите хотя бы одну посылку", "error");
            return;
        }

        const ids = checked.map(cb => cb.value);

        // 🔹 Спрашиваем через кнопки
        let choice = null;
        if (confirm("Скачать Манифест? (Если отмените, будет Опись)")) {
            choice = "манифест";
        } else {
            choice = "опись";
        }

        if (!confirm("თქვენ მართლა გსურთ გადმოწერა?")) return;

        const url = choice === "манифест" ? "/download_manifest" : "/download_inventory";

        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ shipment_ids: ids }),
        })
        .then(response => {
            if (!response.ok) throw new Error();
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = choice === "манифест" ? "manifest.xlsx" : "inventory.xlsx";
            document.body.appendChild(a);
            a.click();

            a.remove();
            window.URL.revokeObjectURL(url);

            showToast("Файл успешно скачан", "success");

            // ✅ Сброс чекбоксов
            checked.forEach(cb => cb.checked = false);
            if (selectAll) selectAll.checked = false;

            // 🔥 Пересчёт выбранных
            updateSelectedInfo();
        })
        .catch(() => {
            showToast("Ошибка при скачивании файла", "error");
        });
    });
});