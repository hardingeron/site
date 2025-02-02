   // Функция открытия модального окна
   function openReservationModal() {
    const modal = document.getElementById('reservationModal');
    modal.style.display = 'flex'; /* Используем flex для центрирования */

    // Инициализация календаря с использованием flatpickr
    const datepicker = flatpickr("#reservationDate", {
      dateFormat: "Y-m-d", // Формат даты
      locale: "ru", // Установка русского языка
    });

    // Добавляем обработчик события на клавишу "Esc"
    window.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closeReservationModal();
      }
    });

    // Добавляем обработчик события на клик вне модального окна
    modal.addEventListener('click', function (event) {
      if (event.target === modal) {
        closeReservationModal();
      }
    });
  }

  // Функция закрытия модального окна
  function closeReservationModal() {
    const modal = document.getElementById('reservationModal');
    modal.style.display = 'none';
  }

  // Функция перенаправления на страницу в зависимости от выбора
  function redirectToReservationPage() {
    const selectedDate = document.getElementById('reservationDate').value;
    const selectedRoute = document.getElementById('routeSelect').value;

    let destination = '/error'; // По умолчанию, если дата не подходит
    if (selectedDate) {
      if (selectedRoute === '1') {
        if (isThursday(selectedDate)) {
          destination = '/reservation?date=' + selectedDate + '&route=1';
        } else if (isSunday(selectedDate)) {
          destination = '/reservation_big?date=' + selectedDate + '&route=1';
        }
      } else if (selectedRoute === '2') {
        if (isWednesday(selectedDate)) {
          destination = '/reservation_big?date=' + selectedDate + '&route=2';
        } else if (isSunday(selectedDate)) {
          destination = '/reservation?date=' + selectedDate + '&route=2';
        }
      }

      // Перенаправляем пользователя на выбранную страницу
      window.location.href = destination;
    }
  }

  // Функция проверки, является ли день четвергом
  function isThursday(dateString) {
    const date = new Date(dateString);
    return date.getDay() === 4; // 4 представляет четверг (0 - воскресенье, 1 - понедельник, и так далее)
  }

  // Функция проверки, является ли день средой
  function isWednesday(dateString) {
    const date = new Date(dateString);
    return date.getDay() === 3; // 3 представляет среду
  }

  // Функция проверки, является ли день воскресеньем
  function isSunday(dateString) {
    const date = new Date(dateString);
    return date.getDay() === 0; // 0 представляет воскресенье
  }