import openpyxl
from openpyxl.styles import Font

def write_to_excel(file_path, data_list):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    start_row = 7
    col_letters = ['C', 'D', 'E', 'F', 'G']

    # Устанавливаем стиль шрифта по умолчанию с размером 10
    font = Font(size=10)
    for row_idx, data in enumerate(data_list, start=start_row):
        for col_idx, col_letter in enumerate(col_letters):
            cell = sheet[f'{col_letter}{row_idx}']
            cell.value = data[col_idx]
            cell.font = font  # Применяем стиль шрифта к ячейке

    new_filename = 'новый_файл.xlsx'
    workbook.save(new_filename)
    workbook.close()

# Пример данных, которые вы хотите добавить
data_to_insert = [
    [ '200', '57001060603', 'დიმიტრი ჯუიშვილი', '15', 'მოსკოვი'],
    [ 'Значение8', 'Значение9', 'Значение10', 'Значение11', 'Значение12'],
    # ... и так далее
]

file_path = 'vedom.xlsx'
write_to_excel(file_path, data_to_insert)
