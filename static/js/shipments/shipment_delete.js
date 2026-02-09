document.addEventListener("click", function (e) {
    if (!e.target.classList.contains("delete-btn")) return;

    const shipmentId = e.target.dataset.id;

    const confirmed = confirm(
        "⚠️ Вы уверены, что хотите удалить эту посылку?\n\nДействие необратимо!"
    );

    if (!confirmed) return;

    fetch(`/shipments/${shipmentId}/delete`, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const card = document.querySelector(
                `.parcel-card[data-shipment-id="${shipmentId}"]`
            );
            if (card) card.remove();
        } else {
            alert("Ошибка при удалении");
        }
    })
    .catch(() => {
        alert("Ошибка соединения с сервером");
    });
});