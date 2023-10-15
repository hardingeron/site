from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash



# Генерация хеша пароля
password = "ViPost_QazEdcQweZxcQscEsz123"  # Замените это на пароль пользователя
hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

# Вывод хеша пароля
print("Хеш пароля:", hashed_password)











#             <div class="payment_block">
#                 <label class="radio-label">
#                     <input type="radio" name="payment" value="paid" required data-error="payment">
#                     <span class="radio-custom">
#                         <img src="/static/images/paid cash.png" alt="Картинка">
#                     </span>
#                 </label>

#                 <label class="radio-label">
#                     <input type="radio" name="payment" value="card">
#                     <span class="radio-custom">
#                         <img src="/static/images/paid card.png" alt="Картинка">
#                     </span>
#                 </label>

#                 <label class="radio-label">
#                     <input type="radio" name="payment" value="not_paid">
#                     <span class="radio-custom">
#                         <img src="/static/images/not paid.png" alt="Картинка">
#                     </span>
#                 </label>
#             </div>































# {% extends 'base.html' %}

# {% block title %}
#     {{ super() }}
#     დამატება
#     {% endblock %}

# {% block content %}
#     <div class="bg-image"></div>
#     <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/style_add.css') }}">
#     <script src="{{ url_for('static', filename='script.js') }}"></script>


#     <div class="add">
#         <div class="add_block">
#             <div class="head">
#                 <h2>დამატება</h2>
#             </div>
#             <input type="text" id="dateInput" name="date" hidden>

#             <div class="sender_block">
#                 <div class="sender_name_block">
#                     <label>გამზავნი</label>
#                     <input type="text" name="sender" required value="" data-error="sender">
#                 </div>
#                 <div class="sender_phone_block">
#                     <label>გამგზავნის ტელ</label>
#                     <input type="text" name="sender_phone" required value="" data-error="sender_phone">                    
#                 </div>
#             </div>
#             <div class="recipient_block">
#                 <div class="recipient_name_block">
#                     <label>მიმღები</label>
#                     <input type="text" name="recipient"  required value="" data-error="recipient">
#                 </div>
#                 <div class="recipient_phone block">
#                     <label>მიმღების ტელ</label>
#                     <input type="text" name="recipient_phone" required value="+7" data-error="recipient_phone">
#                 </div>
#             </div>
#             <div class="description_block">
#                 <label>აღწერა</label>
#                 <textarea name="inventory" required data-error="inventory"></textarea>
#             </div>
#             <div class="information_one_block">
#                 <div class="weight_block">
#                     <label>წონა</label>
#                     <input type="text" name="weight" required  value="" data-error="weight">

#                 </div>
#                 <div class="responsibility_block">
#                     <label>ღირებულება</label>
#                     <input type="text" name="responsibility" value="" data-error="responsibility">
#                 </div>
#                 <div class="passport_block">
#                     <label>პასპორტი</label>
#                     <input type="text" name="passport" value="" data-error="passport">
#                 </div>
#             </div>

#             <div class="information_two_block">
#                 <div class="price">
#                     <label>ფასი</label>
#                     <input type="text" name="cost" required value="" data-error="cost">
#                 </div>
#                 <div class="city">
#                     <label>ქალაქი</label>
#                     <select id="city-select" name="city">
#                         <option value="Moscow">Moscow</option>
#                         <option value="S.P.B">S.P.B</option>
#                     </select>
#                 </div>
#                 <div class="photo_block">
#                     <label>ფოტო</label>
#                     <input type="file" id="photo" required name="photo" class="fandm" data-error="photo">
#                 </div>
#             </div>

#             <div class="payment_block">
#                 <label>
#                     <input type="radio" name="payment" value="paid" required data-error="payment">
#                     <span>+</span>
#                 </label>
#                 <label>
#                     <input type="radio" name="payment" value="not_paid">
#                     <span>-</span>
#                 </label>
#                 <label>
#                     <input type="radio" name="payment" value="card">
#                     <span>ბარათი</span>
#                 </label>
#             </div>
            
#         <div class="button_block">
#             <button id="saveButton" type="button">დასრულება</button>
#         </div>

#     </div>

#     {% for cat, msg in get_flashed_messages(True) %}
#     <div class='flash {{cat}}'>{{msg}}</div>
#     {% endfor %}

    



# <!--  -->
# <script>
#     // Получение параметра URL 'date'
#     const urlParams = new URLSearchParams(window.location.search);
#     const dateParam = urlParams.get('date');

#     // Установка значения в input с id 'dateInput'
#     document.getElementById('dateInput').value = dateParam;
# </script>

# <!--  -->




# <script>
#     document.getElementById('saveButton').addEventListener('click', function() {
#         // Создаем объект данных (FormData)
#         const formData = new FormData();
    
#         // Собираем данные из полей
#         const date = document.querySelector('input[name="date"]').value;
#         const sender = document.querySelector('input[name="sender"]');
#         const senderValue = sender.value;
#         const senderPhone = document.querySelector('input[name="sender_phone"]');
#         const senderPhoneValue = senderPhone.value;
#         const recipient = document.querySelector('input[name="recipient"]');
#         const recipientValue = recipient.value;
#         const recipientPhone = document.querySelector('input[name="recipient_phone"]');
#         const recipientPhoneValue = recipientPhone.value;
#         const inventory = document.querySelector('textarea[name="inventory"]');
#         const inventoryValue = inventory.value;
#         const weight = document.querySelector('input[name="weight"]');
#         const weightValue = weight.value;
#         const responsibility = document.querySelector('input[name="responsibility"]');
#         const responsibilityValue = responsibility.value;
#         const passport = document.querySelector('input[name="passport"]');
#         const passportValue = passport.value;
#         const cost = document.querySelector('input[name="cost"]');
#         const costValue = cost.value;
#         const city = document.querySelector('select[name="city"]');
#         const cityValue = city.value;
#         const payment = document.querySelector('input[name="payment"]:checked');
#         const paymentValue = payment ? payment.value : '';
    
#         // Проверка каждого поля на заполнение
#         const requiredFields = [
#             { field: sender, value: senderValue, error: 'sender' },
#             { field: senderPhone, value: senderPhoneValue, error: 'sender_phone' },
#             { field: recipient, value: recipientValue, error: 'recipient' },
#             { field: recipientPhone, value: recipientPhoneValue, error: 'recipient_phone' },
#             { field: inventory, value: inventoryValue, error: 'inventory' },
#             { field: weight, value: weightValue, error: 'weight' },
#             { field: responsibility, value: responsibilityValue, error: 'responsibility' },
#             { field: passport, value: passportValue, error: 'passport' },
#             { field: cost, value: costValue, error: 'cost' },
#             { field: city, value: cityValue, error: 'city' },
#             { field: payment, value: paymentValue, error: 'payment' },
#         ];
    
#         let isValid = true;
    
#         for (const { field, value, error } of requiredFields) {
#             if (value === "") {
#                 // Если поле пустое, устанавливаем флаг недопустимости
#                 isValid = false;
#                 // Изменяем цвет границы поля, если поле существует
#                 if (field) {
#                     field.style.border = '1px solid red';
#                 }
#                 // Здесь вы можете предпринять дополнительные действия в случае ошибки, например, показать сообщение об ошибке
#                 showMessage(`შეავსეთ მითითებული ველები!`, false);
    
#                 // Вернуть цвет границы к исходному состоянию через 2 секунды
#                 setTimeout(() => {
#                     if (field) {
#                         field.style.border = '1px solid #ccc'; // Замените #ccc на цвет по умолчанию, если он отличается
#                     }
#                 }, 2000); // 2000 миллисекунд = 2 секунды
#             }
#         }
    
#         if (isValid) {
#             // Оставшаяся часть вашего кода для отправки данных
#             formData.append('date', date);
#             formData.append('sender', senderValue);
#             formData.append('sender_phone', senderPhoneValue);
#             formData.append('recipient', recipientValue);
#             formData.append('recipient_phone', recipientPhoneValue);
#             formData.append('inventory', inventoryValue);
#             formData.append('weight', weightValue);
#             formData.append('responsibility', responsibilityValue);
#             formData.append('passport', passportValue);
#             formData.append('cost', costValue);
#             formData.append('city', cityValue);
#             formData.append('payment', paymentValue);
    
#             // Получение файла (фото)
#             const photoInput = document.getElementById('photo');
#             const photoFile = photoInput.files[0];
    
#             if (!photoFile) {
#                 alert('Выберите фото');
#                 return; // Останавливаем выполнение функции
#             }
    
#             formData.append('photo', photoFile);
    
#             // Отправляем данные на сервер с использованием AJAX
#             fetch('/saving_a_parcel', {
#                 method: 'POST',
#                 body: formData
#             })
#             .then(response => response.json())
#             .then(data => {
#                 // Проверка флага success
#                 if (data.success) {
#                     // Очистить поля ввода и показать сообщение об успешном сохранении
#                     showMessage(data.message + ':' + data.parcelNumber, true);

#                     // Очистить поля ввода
#                     document.querySelector('input[name="sender"]').value = '';
#                     document.querySelector('input[name="sender_phone"]').value = '';
#                     document.querySelector('input[name="recipient"]').value = '';
#                     document.querySelector('input[name="recipient_phone"]').value = '';
#                     document.querySelector('textarea[name="inventory"]').value = '';
#                     document.querySelector('input[name="weight"]').value = '';
#                     document.querySelector('input[name="responsibility"]').value = '';
#                     document.querySelector('input[name="passport"]').value = '';
#                     document.querySelector('input[name="cost"]').value = '';

#                     // Очистить файловое поле (фото)
#                     const photoInput = document.getElementById('photo');
#                     photoInput.value = ''; // Очистить поле ввода файла
#                 } else {
#                     // Показать сообщение об ошибке
#                     showMessage(data.message, false);
#                 }
#             })
#             .catch(error => {
#                 console.error('Ошибка:', error);
#             });
#         }
#     });
#     </script>





#     </body>

# {% endblock %}