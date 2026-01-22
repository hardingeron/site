
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

        if (!confirm("თქვენ მართლა გსურთ მანიფესტის გადმოწერა?")) return;

        fetch("/download_manifest", {
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
            a.download = "manifest.xlsx";
            document.body.appendChild(a);
            a.click();

            a.remove();
            window.URL.revokeObjectURL(url);

            showToast("Файл успешно скачан", "success");

            // ✅ СБРОС ЧЕКБОКСОВ
            checked.forEach(cb => cb.checked = false);
            if (selectAll) selectAll.checked = false;

            // 🔥 ПЕРЕСЧЁТ (ВАЖНО)
            updateSelectedInfo();
        })
        .catch(() => {
            showToast("Ошибка при скачивании файла", "error");
        });
    });
});

