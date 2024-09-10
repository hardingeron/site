document.addEventListener('DOMContentLoaded', function() {
    flatpickr(".select_date", {
        dateFormat: "Y-m-d",
        locale: "ru",
        confirmDate: true,
        onChange: function(selectedDates, dateStr, instance) {
            window.location.href = "/expertise?selected_date=" + dateStr;
        }
   });
});
