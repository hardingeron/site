document.getElementById('searchByName').addEventListener('click', function () {
    const fullName = document.getElementById('nameInput').value.trim();
    if (!fullName) {
        alert('ჩაწერეთ სახელი და გვარი');
        return;
    }

    fetch('/search_by_name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullName })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    alert(errorData.error);
                    throw new Error(errorData.error);
                });
            }
            return response.json();
        })
        .then(data => {
            const tableBody = document.getElementById('parcelTableBody');
            tableBody.innerHTML = ''; // Очищаем таблицу перед новым выводом

            if (data.length > 0) {
                const passport = data[0].passport || 'მონაცემები არ არის';
                document.getElementById('passport').value = passport;
            } else {
                document.getElementById('passport').value = '';
                alert('მონაცემები არ არის');
            }

            data.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = ` 
                    <td><input class="form-check-input" type="checkbox"></td>
                    <td>${record.tracking}</td>
                    <td>${record.recipient}</td>
                    <td>${record.weight} კგ</td>
                    <td>${record.days_ago}</td>
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




















