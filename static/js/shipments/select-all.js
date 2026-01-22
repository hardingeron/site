// выделение/снятие всех чекбоксов посылок 
document.addEventListener("DOMContentLoaded", () => {
    const selectAll = document.getElementById("selectAllShipments");
    const checkboxes = document.querySelectorAll('input[name="selected_shipments"]');

    selectAll.addEventListener("change", () => {
        const checked = selectAll.checked;
        checkboxes.forEach(cb => cb.checked = checked);
    });
});