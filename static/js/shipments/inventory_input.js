document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("inventoryInput");
    const container = document.getElementById("inventoryContainer");
    const autocompleteList = document.getElementById("autocompleteList");

    const inventory = JSON.parse(input.dataset.inventory);

    let currentName = "";
    let currentNumber = "";
    let selectedFromList = false;

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

    function applyInlineAutocomplete(match, typed) {
        input.value = match;
        input.setSelectionRange(typed.length, match.length);
        selectedFromList = true;
    }

    input.addEventListener("input", () => {
        const val = input.value;

        // если уже начали вводить число — не мешаем
        if (val.includes(":")) {
            const parts = val.split(/:\s?/);
            currentName = parts[0].trim();
            currentNumber = parts[1] ? parts[1].trim() : "";

            if (currentNumber && !isValidNumber(currentNumber)) {
                currentNumber = currentNumber.slice(0, -1);
                input.value = currentName + ": " + currentNumber;
            }

            autocompleteList.style.display = "none";
            return;
        }

        currentName = val.trim();
        currentNumber = "";

        if (!currentName) {
            autocompleteList.style.display = "none";
            return;
        }

        const matches = inventory.filter(item =>
            item.toLowerCase().startsWith(currentName.toLowerCase())
        );

        if (matches.length > 0) {
            const bestMatch = matches[0];
            applyInlineAutocomplete(bestMatch, currentName);
        }
    });

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();

            if (input.value && !input.value.includes(":")) {
                input.value = input.value + ": ";
                selectedFromList = false;
                return;
            }

            if (currentName && (selectedFromList || currentNumber)) {
                addTag(currentName, currentNumber);
                input.value = "";
                currentName = "";
                currentNumber = "";
                selectedFromList = false;
            }
        }

        // если пользователь стирает — убираем автодополнение
        if (e.key === "Backspace") {
            selectedFromList = false;
        }
    });

    document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !container.contains(e.target)) {
            autocompleteList.style.display = "none";
        }
    });
});
