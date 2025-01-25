document.getElementById('searchButton').addEventListener('click', function () {
    const recipient = document.getElementById('recipient').value.trim();
    if (!recipient) {
        alert('Введите получателя');
        return;
    }

    fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recipient })
    })
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('parcelTableBody');
            tableBody.innerHTML = ''; // Очищаем таблицу

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
                            ${record.issued ? 'Выдана' : 'Не выдана'}
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Ошибка:', error));
});
