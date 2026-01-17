document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("inventoryInput");
    const container = document.getElementById("inventoryContainer");
    const autocompleteList = document.getElementById("autocompleteList");

    const inventory = JSON.parse(input.dataset.inventory);

    let currentName = "";   // текст до :
    let currentNumber = ""; // число после :
    let selectedFromList = false; // выбрал подсказку?

    function isValidNumber(input) {
        return /^\d+(\.\d{0,2})?$/.test(input);
    }

    function addTag(name, number) {
        const tag = document.createElement("div");
        tag.classList.add("inventory-tag");

        const span = document.createElement("span");
        span.textContent = number ? `${name}: ${number}` : `${name}: `;

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => container.removeChild(tag));

        tag.appendChild(span);
        tag.appendChild(removeBtn);
        container.appendChild(tag);
    }

    function showAutocomplete(matches) {
        autocompleteList.innerHTML = "";
        if (matches.length === 0) {
            autocompleteList.style.display = "none";
            return;
        }

        matches.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            li.addEventListener("click", () => {
                currentName = item;
                selectedFromList = true;
                input.value = currentName + ": ";
                input.focus();
                autocompleteList.style.display = "none";
            });
            autocompleteList.appendChild(li);
        });
        autocompleteList.style.display = "block";
    }

    input.addEventListener("input", () => {
        const val = input.value;
        const parts = val.split(/:\s?/);
        currentName = parts[0].trim();
        currentNumber = parts[1] ? parts[1].trim() : "";

        // проверка числа
        if (parts.length > 1 && currentNumber && !isValidNumber(currentNumber)) {
            currentNumber = currentNumber.slice(0, -1);
            input.value = currentName + ": " + currentNumber;
        }

        // автодополнение только если не начали вводить число
        if (!currentNumber) {
            const matches = inventory.filter(item =>
                item.toLowerCase().startsWith(currentName.toLowerCase()) &&
                item.toLowerCase() !== currentName.toLowerCase()
            );
            showAutocomplete(matches);
        } else {
            autocompleteList.style.display = "none";
        }
    });

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();

            // если выбрали из списка или уже есть число
            if (selectedFromList || currentNumber) {
                addTag(currentName, currentNumber);
                input.value = "";
                currentName = "";
                currentNumber = "";
                selectedFromList = false;
                autocompleteList.style.display = "none";
            } else {
                // если не выбрали из списка → просто ставим : и пробел
                if (!input.value.endsWith(": ")) {
                    input.value = currentName + ": ";
                }
            }
        }

        if (e.key === "Backspace" && currentNumber) {
            currentNumber = currentNumber.slice(0, -1);
            input.value = currentName + ": " + currentNumber;
            e.preventDefault();
        }
    });

    document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !container.contains(e.target)) {
            autocompleteList.style.display = "none";
        }
    });
});
