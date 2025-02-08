$(document).ready(function () {
    $('.menu-item').on('click', function () {
        if ($(this).text().trim() === "- პეტერბურგი") {
            loadSpbData();
        }
    });
});

function loadSpbData() {
    $('#spb-loading').show(); // Показываем сообщение о загрузке

    $.ajax({
        url: "/spb_data",
        method: "POST",
        dataType: "json",
        success: function (response) {
            $('#spb-loading').hide(); // Скрываем загрузку
            renderSpbChart(response);
        },
        error: function () {
            $('#spb-loading').text("Ошибка загрузки данных");
        }
    });
}

function renderSpbChart(data) {
    let ctx = document.getElementById("spbChart").getContext("2d");


    // Создание градиентов для фона
    let gradientWeight = ctx.createLinearGradient(0, 0, 0, 400);
    gradientWeight.addColorStop(0, 'rgba(255, 99, 132, 0.8)');
    gradientWeight.addColorStop(1, 'rgba(255, 99, 132, 0.2)');

    let gradientPackages = ctx.createLinearGradient(0, 0, 0, 400);
    gradientPackages.addColorStop(0, 'rgba(54, 162, 235, 0.8)');
    gradientPackages.addColorStop(1, 'rgba(54, 162, 235, 0.2)');

    let gradientProfitLari = ctx.createLinearGradient(0, 0, 0, 400);
    gradientProfitLari.addColorStop(0, 'rgba(255, 206, 86, 0.8)');
    gradientProfitLari.addColorStop(1, 'rgba(255, 206, 86, 0.2)');

    let gradientProfitRub = ctx.createLinearGradient(0, 0, 0, 400);
    gradientProfitRub.addColorStop(0, 'rgba(75, 192, 192, 0.8)');
    gradientProfitRub.addColorStop(1, 'rgba(75, 192, 192, 0.2)');

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.months,
            datasets: [
                { 
                    label: "Вес (кг)", 
                    data: data.weight, 
                    backgroundColor: gradientWeight,
                    borderColor: "rgba(255, 99, 132, 1)", // Обводка столбцов
                    borderWidth: 2,
                    hoverBackgroundColor: "rgba(255, 99, 132, 0.9)", // Цвет при наведении
                },
                { 
                    label: "Количество посылок", 
                    data: data.packages, 
                    backgroundColor: gradientPackages,
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 2,
                    hoverBackgroundColor: "rgba(54, 162, 235, 0.9)",
                },
                { 
                    label: "Прибыль (лари)", 
                    data: data.profit_lari, 
                    backgroundColor: gradientProfitLari,
                    borderColor: "rgba(255, 206, 86, 1)",
                    borderWidth: 2,
                    hoverBackgroundColor: "rgba(255, 206, 86, 0.9)",
                },
                { 
                    label: "Прибыль (руб)", 
                    data: data.profit_rub, 
                    backgroundColor: gradientProfitRub,
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 2,
                    hoverBackgroundColor: "rgba(75, 192, 192, 0.9)",
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 10, // Шаг оси Y
                    },
                },
                x: {
                    ticks: {
                        autoSkip: false, // Показывать все метки по оси X
                        maxRotation: 45, // Поворот меток для лучшей читаемости
                        minRotation: 45,
                    }
                }
            },
            plugins: {
                legend: {
                    display: true, // Показать легенду
                    position: 'top', // Расположение легенды
                    labels: {
                        font: {
                            size: 14, // Размер шрифта в легенде
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)', // Цвет фона подсказки
                    titleFont: {
                        size: 16, // Размер шрифта в заголовке подсказки
                    },
                    bodyFont: {
                        size: 14, // Размер шрифта в теле подсказки
                    }
                }
            },
            animation: {
                duration: 1000, // Время анимации
                easing: 'easeOutBounce' // Эффект анимации
            }
        }
    });
}