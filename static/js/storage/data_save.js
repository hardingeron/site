$(document).ready(function() {
    $('#add_trecing').focus();

    $('#add-form').submit(function(event) {
        event.preventDefault(); 

        var formData = $(this).serialize(); 

        $.ajax({
            type: 'POST',
            url: '/save',
            data: formData,
            success: function(response) {
                if (response.success === false) {
                    showMessage(response.message, false);
                } else {
                    $('#add_trecing').val(''); // Очищаем поле текстовой области
                    $('#add_trecing').focus(); 
                }
            },
            error: function() {
                console.log('Ошибка при выполнении AJAX-запроса');
            }
        });
    });

    $('#add_trecing').on('input', function() {
        var inputValue = $(this).val().trim();
        var match = inputValue.match(/\|(.*?)\\/);

        if (match) {
            var shelfValue = match[1];

            $('#add_shelf').val(shelfValue); // Устанавливаем значение на клиенте

            $('#add-form').submit();
        }
    });
});
