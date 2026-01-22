/* =========================
   ГЛОБАЛЬНЫЙ ПОДСЧЁТ
========================= */

function updateSelectedInfo() {
    const checkboxes = document.querySelectorAll('input[name="selected_shipments"]');
    const selectedInfo = document.getElementById("selectedInfo");

    if (!selectedInfo) return;

    let totalParcels = 0;
    let totalWeight = 0;

    checkboxes.forEach(cb => {
        if (cb.checked) {
            const parcels = parseInt(cb.dataset.parcels) || 0;
            const weight = parseFloat(cb.dataset.weight) || 0;

            totalParcels += parcels;
            totalWeight += weight;
        }
    });

    selectedInfo.textContent = `${totalParcels} шт / ${totalWeight.toFixed(2)} кг`;
}

/* =========================
   ИНИЦИАЛИЗАЦИЯ
========================= */

document.addEventListener("DOMContentLoaded", () => {
    const selectAll = document.getElementById("selectAllShipments");
    const checkboxes = document.querySelectorAll('input[name="selected_shipments"]');

    // отдельные чекбоксы
    checkboxes.forEach(cb => {
        cb.addEventListener("change", () => {
            updateSelectedInfo();

            if (selectAll) {
                selectAll.checked = Array.from(checkboxes).every(c => c.checked);
            }
        });
    });

    // "выделить все"
    if (selectAll) {
        selectAll.addEventListener("change", () => {
            const checked = selectAll.checked;
            checkboxes.forEach(cb => cb.checked = checked);
            updateSelectedInfo();
        });
    }

    // стартовое состояние
    updateSelectedInfo();
});