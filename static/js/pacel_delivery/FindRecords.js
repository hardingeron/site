document.getElementById('searchButton').addEventListener('click', function () {
    const recipient = document.getElementById('recipient').value.trim();
    if (!recipient) {
        alert('ჩაწერეთ თრექინგი');
        return;
    }

    fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recipient })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    alert(errorData.error);  // Показываем сообщение об ошибке
                    throw new Error(errorData.error);
                });
            }
            return response.json();
        })
        .then(data => {
            const tableBody = document.getElementById('parcelTableBody');
            tableBody.innerHTML = ''; // Очищаем таблицу

            if (data.length > 0) {
                // Предположим, что первый элемент данных содержит нужный паспорт
                const passport = data[0].passport || 'მონაცემები არ არის';
                document.getElementById('passport').value = passport; // Устанавливаем значение в поле ввода
            } else {
                document.getElementById('passport').value = ''; // Очищаем поле, если данных нет
                alert('მონაცემები არ არის');
            }

            data.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = ` 
                    <td><input class="form-check-input" type="checkbox"></td>
                    <td>${record.tracking}</td>
                    <td>${record.recipient}</td>
                    <td>${record.weight} кг</td>
                    <td>${record.date}</td>
                    <td>
                        <button class="btn ${record.issued ? 'btn-success' : 'btn-danger'} btn-sm btn-status" disabled>
                            ${record.issued ? 'გაცემულია' : 'გასაცემია'}
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Ошибка:', error));
});
