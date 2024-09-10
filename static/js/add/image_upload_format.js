    // Функция для обработки выбранного изображения
    function handleImageUpload(event) {
        const file = event.target.files[0];

        // Создаем объект FileReader
        const reader = new FileReader();

        // Устанавливаем функцию обратного вызова для обработки прочитанных данных
        reader.onload = function(event) {
            const image = new Image();
            image.src = event.target.result;

            // Устанавливаем желаемое разрешение (например, 800x600)
            const desiredWidth = 800;
            const desiredHeight = 600;

            // Создаем элемент canvas для изменения разрешения
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            // Устанавливаем новые размеры canvas
            canvas.width = desiredWidth;
            canvas.height = desiredHeight;

            // Отрисовываем изображение на canvas с новым разрешением
            ctx.drawImage(image, 0, 0, desiredWidth, desiredHeight);

            // Преобразуем изображение обратно в формат data URL
            const resizedImageDataURL = canvas.toDataURL('image/jpeg', 0.7); // Устанавливаем качество сжатия (от 0 до 1)

            // Здесь вы можете использовать resizedImageDataURL для дальнейшей обработки или отображения на странице
            console.log(resizedImageDataURL);
        };

        // Читаем данные изображения как data URL
        reader.readAsDataURL(file);
    }

    // Назначаем обработчик события изменения input file
    document.getElementById('photo').addEventListener('change', handleImageUpload);