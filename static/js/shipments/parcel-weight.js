document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("parcelWeight");
    const container = document.getElementById("weightContainer");
    const hiddenInput = document.getElementById("weightsHidden");

    // число: цифры + 1 точка + максимум 2 знака после точки
    function isValidWeight(value) {
        return /^\d+(\.\d{0,2})?$/.test(value);
    }

    // приводим к формату с 2 знаками после точки
    function formatWeight(value) {
        let num = parseFloat(value);
        if (isNaN(num)) return "0.00";
        return num.toFixed(2); // всегда два знака после точки
    }

    // обновляем hidden для Flask
    function updateHiddenWeights() {
        const weights = [];
        container.querySelectorAll(".weight-tag").forEach(tag => {
            weights.push(tag.textContent);
        });
        hiddenInput.value = weights.join(" ");
    }

    function addWeightTag(value) {
        const formattedValue = formatWeight(value);

        const tag = document.createElement("div");
        tag.classList.add("weight-tag");
        tag.textContent = formattedValue;

        container.appendChild(tag);
        updateHiddenWeights();
    }

    input.addEventListener("input", () => {
        let value = input.value;

        // запрещаем всё, кроме валидного числа
        if (!isValidWeight(value)) {
            input.value = value.slice(0, -1);
        }
    });

    input.addEventListener("keydown", (e) => {
        // ENTER — зафиксировать вес
        if (e.key === "Enter") {
            e.preventDefault();

            let value = input.value.trim();
            if (!value) return;

            // если пользователь ввел просто "12." → addWeightTag добавит 12.00 автоматически
            addWeightTag(value);
            input.value = "";
        }

        // BACKSPACE
        if (e.key === "Backspace" && input.value === "") {
            const lastTag = container.lastElementChild;
            if (lastTag) {
                container.removeChild(lastTag);
                updateHiddenWeights();
            }
        }
    });
});
