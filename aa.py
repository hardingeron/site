import random

# Слова для игры
words = ["python", "programming", "hangman", "code", "developer", "computer"]

# Выбираем случайное слово
word = random.choice(words)
word = word.lower()  # Преобразуем в нижний регистр

# Инициализируем переменные
guessed = ["_"] * len(word)
attempts = 6  # Количество попыток

# Основной игровой цикл
while attempts > 0:
    print(" ".join(guessed))
    letter = input("Угадайте букву: ").lower()

    if letter in word:
        print("Правильно!")
        for i in range(len(word)):
            if word[i] == letter:
                guessed[i] = letter
    else:
        print("Неправильно!")
        attempts -= 1

    if "".join(guessed) == word:
        print(f"Поздравляем, вы угадали слово: {word}")
        break

if attempts == 0:
    print(f"Вы проиграли. Загаданное слово было: {word}")
