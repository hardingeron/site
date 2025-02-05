$(document).ready(function () {
    $('.menu-item').on('click', function () {
        if ($(this).text().trim() === "Анализ Тбилиси") {
            loadTbilisiData();
        }
    });
});

function loadTbilisiData() {
    $('#tbilisi-loading').show(); // Показываем сообщение о загрузке

    $.ajax({
        url: "/tbilisi_data",
        method: "POST",  // Был GET, меняем на POST
        dataType: "json",
        success: function (response) {
            $('#tbilisi-loading').hide();
            renderTbilisiChart(response);
        },
        error: function () {
            $('#tbilisi-loading').text("Ошибка загрузки данных");
        }
    });
}

function renderTbilisiChart(data) {
    let ctx = document.getElementById("tbilisiChart").getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.months,
            datasets: [
                { label: "Вес (кг)", data: data.weight, backgroundColor: "rgba(255, 99, 132, 0.6)" },
                { label: "Количество посылок", data: data.packages, backgroundColor: "rgba(54, 162, 235, 0.6)" },
                { label: "Прибыль (лари)", data: data.profit_lari, backgroundColor: "rgba(255, 206, 86, 0.6)" },
                { label: "Прибыль (руб)", data: data.profit_rub, backgroundColor: "rgba(75, 192, 192, 0.6)" }
            ]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}
