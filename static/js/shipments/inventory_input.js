document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("inventoryInput");
    const container = document.getElementById("inventoryContainer");
    const weightContainer = document.getElementById("weightContainer"); 

    const inventory = JSON.parse(input.dataset.inventory);

    let currentName = "";
    let currentNumber = "";
    let inlineSelected = false;
    let isDeleting = false;

    // Лейбл с доступным весом
    let weightLabel = document.createElement("div");
    weightLabel.style.color = "blue";
    weightLabel.style.marginTop = "5px";
    input.parentNode.appendChild(weightLabel);

    // Блок для ошибок
    let weightErrorDiv = document.createElement("div");
    weightErrorDiv.style.color = "red";
    weightErrorDiv.style.marginTop = "5px";
    weightErrorDiv.style.transition = "opacity 0.3s ease";
    weightErrorDiv.style.opacity = 0;
    input.parentNode.appendChild(weightErrorDiv);

    function getMaxTotalWeight() {
        let total = 0;
        weightContainer.querySelectorAll(".weight-tag").forEach(tag => {
            const num = parseFloat(tag.textContent);
            if (!isNaN(num)) total += num;
        });
        return total;
    }

    function currentTotalWeight() {
        let total = 0;
        container.querySelectorAll(".inventory-tag span").forEach(span => {
            const text = span.textContent.split(":")[1].trim();
            const num = parseFloat(text);
            if (!isNaN(num)) total += num;
        });
        return total;
    }

    function updateWeightLabel() {
        let available = getMaxTotalWeight() - currentTotalWeight();
        if (available < 0) available = 0;
        weightLabel.textContent = `Доступно ещё ${available.toFixed(2)} кг`;
    }

    function showWeightError(message) {
        weightErrorDiv.textContent = message;
        weightErrorDiv.style.opacity = 1;
        setTimeout(() => {
            weightErrorDiv.style.opacity = 0;
        }, 3000);
    }

    function addTag(name, number) {
        const numValue = parseFloat(number);

        if (!numValue || numValue <= 0) {
            showWeightError("Вес должен быть больше 0!");
            return;
        }

        const totalUsed = currentTotalWeight();
        const maxTotal = getMaxTotalWeight();

        if (totalUsed + numValue > maxTotal) {
            showWeightError(`Превышен допустимый вес! Доступно ещё ${(maxTotal - totalUsed).toFixed(2)} кг.`);
            return;
        }

        const tag = document.createElement("div");
        tag.classList.add("inventory-tag");

        const span = document.createElement("span");
        span.textContent = `${name}: ${numValue.toFixed(2)}`;

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => {
            container.removeChild(tag);
            updateWeightLabel();
        });

        tag.appendChild(span);
        tag.appendChild(removeBtn);
        container.appendChild(tag);

        updateWeightLabel();
    }

    // ------------------- INLINE AUTOCOMPLETE -------------------
    function getBestMatch(typed) {
        if (!typed) return null;
        const match = inventory.find(item => item.toLowerCase().startsWith(typed.toLowerCase()));
        return match || null;
    }

    input.addEventListener("keydown", (e) => {
        const val = input.value;

        // Удаление
        if (e.key === "Backspace" || e.key === "Delete") {
            isDeleting = true;
            inlineSelected = false;
        }

        // Ввод веса после :
        if (val.includes(":")) {
            const allowedKeys = ["Backspace", "Delete", "ArrowLeft", "ArrowRight", "Tab"];
            const weightPart = val.split(":")[1] || "";

            if (!allowedKeys.includes(e.key)) {
                if (!/^\d$/.test(e.key) && e.key !== ".") {
                    e.preventDefault();
                }
                // запрещаем больше одной точки
                if (e.key === "." && weightPart.includes(".")) {
                    e.preventDefault();
                }
                // запрещаем больше 2 цифр после точки
                const dotIndex = weightPart.indexOf(".");
                if (dotIndex !== -1 && weightPart.length - dotIndex > 2 && /^\d$/.test(e.key)) {
                    e.preventDefault();
                }
            }
        }

        // Enter
        if (e.key === "Enter") {
            e.preventDefault();
            if (!val.includes(":")) {
                input.value = val + ": ";
                inlineSelected = false;
                return;
            }

            const parts = val.split(/:\s?/);
            currentName = parts[0].trim();
            currentNumber = parts[1] ? parts[1].trim() : "";

            // Приведение числа к формату X.00
            let num = parseFloat(currentNumber);
            if (isNaN(num)) num = 0;
            currentNumber = num.toFixed(2);

            if (currentName && currentNumber) {
                addTag(currentName, currentNumber);
                input.value = "";
                inlineSelected = false;
            }
        }
    });

    input.addEventListener("input", () => {
        const val = input.value;

        if (val.includes(":")) {
            inlineSelected = false;
            return;
        }

        currentName = val.trim();
        if (!currentName) return;

        const cursorPos = input.selectionStart;

        // автодополнение только если курсор в конце и не происходит удаление
        if (cursorPos !== val.length || isDeleting) {
            isDeleting = false;
            return;
        }

        const match = getBestMatch(currentName);
        if (match && match.toLowerCase() !== currentName.toLowerCase()) {
            input.value = match;
            input.setSelectionRange(currentName.length, match.length);
            inlineSelected = true;
        } else {
            inlineSelected = false;
        }
    });

    // ------------------- Инициализация -------------------
    window.initInventoryWeightLabel = () => {
        updateWeightLabel();
    };
    updateWeightLabel();
});