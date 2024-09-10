$('#find-form').submit(function(event) {
    event.preventDefault();

    var formData = $(this).serialize();

    $.ajax({
        type: 'POST',
        url: '/find',
        data: formData,
        success: function(response) {
            var location = response.shelf;

            $('#location-container').html('<input type="text" name="shelf" id="find_shelf" readonly value="' + location + '" class="form-control">');
            $('#find_trecing').val('');
            $('#result-container').html(response.otherData);
            $('#find_trecing').focus();
        },
        error: function() {
            console.log('Ошибка при выполнении AJAX-запроса');
        }
    });
});