var filterNumberInput = document.getElementById('filter-number');
var filterSenderInput = document.getElementById('filter-sender');
var filterSenderPhoneInput = document.getElementById('filter-sender-phone');
var filterRecipientInput = document.getElementById('filter-recipient');
var filterRecipientPhoneInput = document.getElementById('filter-recipient-phone');
var filterCostInput = document.getElementById('filter-cost');
var filterWeightInput = document.getElementById('filter-weight');
var filterCityInput = document.getElementById('filter-city');
var filterFlightInput = document.getElementById('filter-flight');
var filterWhereFromInput = document.getElementById('filter-where_from');

// Обработчик события ввода в поля фильтров
filterNumberInput.addEventListener('input', filterTable);
filterSenderInput.addEventListener('input', filterTable);
filterSenderPhoneInput.addEventListener('input', filterTable);
filterRecipientInput.addEventListener('input', filterTable);
filterRecipientPhoneInput.addEventListener('input', filterTable);
filterCostInput.addEventListener('input', filterTable);
filterWeightInput.addEventListener('input', filterTable);
filterCityInput.addEventListener('input', filterTable);
filterFlightInput.addEventListener('input', filterTable);
filterWhereFromInput.addEventListener('input', filterTable);

function filterTable() {
var filterNumberValue = filterNumberInput.value.toLowerCase();
var filterSenderValue = filterSenderInput.value.toLowerCase();
var filterSenderPhoneValue = filterSenderPhoneInput.value.toLowerCase();
var filterRecipientValue = filterRecipientInput.value.toLowerCase();
var filterRecipientPhoneValue = filterRecipientPhoneInput.value.toLowerCase();
var filterCostValue = filterCostInput.value.toLowerCase();
var filterWeightValue = filterWeightInput.value.toLowerCase();
var filterCityValue = filterCityInput.value.toLowerCase();
var filterFlightValue = filterFlightInput.value.toLowerCase();
var filterWhereFromValue = filterWhereFromInput.value.toLowerCase();

var tableRows = document.querySelectorAll('.table tbody tr');

tableRows.forEach(function(row) {
    var numberCell = row.querySelector('.number');
    var senderCell = row.querySelectorAll('td')[2];
    var senderPhoneCell = row.querySelectorAll('td')[3];
    var recipientCell = row.querySelectorAll('td')[4];
    var recipientPhoneCell = row.querySelectorAll('td')[5];
    var costCell = row.querySelectorAll('td')[6];
    var weightCell = row.querySelectorAll('td')[7];
    var cityCell = row.querySelectorAll('td')[8];
    var flightCell = row.querySelectorAll('td')[9];
    var whereFromCell = row.querySelectorAll('td')[10];

    var numberValue = numberCell.textContent.toLowerCase();
    var senderValue = senderCell.textContent.toLowerCase();
    var senderPhoneValue = senderPhoneCell.textContent.toLowerCase();
    var recipientValue = recipientCell.textContent.toLowerCase();
    var recipientPhoneValue = recipientPhoneCell.textContent.toLowerCase();
    var costValue = costCell.textContent.toLowerCase();
    var weightValue = weightCell.textContent.toLowerCase();
    var cityValue = cityCell.textContent.toLowerCase();
    var flightValue = flightCell.textContent.toLowerCase();
    var whereFromValue = whereFromCell.textContent.toLowerCase();

    if (numberValue.includes(filterNumberValue) &&
        senderValue.includes(filterSenderValue) &&
        senderPhoneValue.includes(filterSenderPhoneValue) &&
        recipientValue.includes(filterRecipientValue) &&
        recipientPhoneValue.includes(filterRecipientPhoneValue) &&
        costValue.includes(filterCostValue) &&
        weightValue.includes(filterWeightValue) &&
        cityValue.includes(filterCityValue) &&
        flightValue.includes(filterFlightValue) &&
        whereFromValue.includes(filterWhereFromValue)) {
        row.style.display = ''; // Показываем строку, если соответствует фильтру
    } else {
        row.style.display = 'none'; // Скрываем строку, если не соответствует фильтру
    }
});
}