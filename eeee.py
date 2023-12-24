# import json

# # Загрузка данных из JSON-файла
# with open('expertise_data.json', 'r', encoding='utf-8') as json_file:
#     data = json.load(json_file)

# # Ключ, который вы передаете событию (замените 'ваш_ключ' на актуальный ключ)
# selected_key = 'MP67722768'

# # Извлекаем данные для выбранного ключа
# selected_data = data.get(selected_key)

# # Проверяем дубликаты для данных [3] и [5]
# if selected_data:
#     data_key_3 = selected_data[3]  # Данные [3]
#     data_key_5 = selected_data[5]  # Данные [5]

#     # Ищем дубликаты
#     duplicates = [key for key, value in data.items() if key != selected_key and value[3] == data_key_3 and value[5] == data_key_5]

#     # Выводим результат
#     print(f'Данные [3] и [5] выбранного ключа: {data_key_3}, {data_key_5}')
#     if duplicates:
#         print(f'Найдены дубликаты в других ключах: {duplicates}')
#     else:
#         print('Дубликатов не найдено')
# else:
#     print(f'Ключ {selected_key} не найден в данных.')



expertise_list = {}



n = {
    'id': "new_record.id",
    'status': "new_record.status",
    'recipient': "new_record.recipient",
    'weight': "new_record.weight",
    'Number': "new_record.Number",
    'tracking': "new_record.tracking",
    'comment': "new_record.comment",
    'date': "new_record.date.strftime('%Y-%m-%d')"
}
print(n)
expertise_list.append(n)
    