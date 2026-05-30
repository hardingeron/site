(function () {
    const settingsUrl = window.documentSettingsUrl || "/document_settings";
    const supportedCurrencies = new Set(["GEL", "RUB"]);

    let priceSettings = null;
    let priceSettingsRequest = null;

    function parseNumber(value) {
        const parsed = parseFloat(String(value || "").replace(",", "."));
        return Number.isFinite(parsed) ? parsed : null;
    }

    function getSelectedCurrency() {
        const selectedCurrency = document.querySelector("input[name='payment_currency']:checked");
        return selectedCurrency ? selectedCurrency.value : null;
    }

    function getCityKey(city) {
        const normalizedCity = String(city || "").toLowerCase().replace(/[\s.]/g, "");

        if (normalizedCity === "moscow") {
            return "moscow";
        }

        if (normalizedCity === "spb") {
            return "spb";
        }

        return null;
    }

    function roundGel(amount) {
        const floorAmount = Math.floor(amount);
        return amount - floorAmount > 0.5 ? Math.ceil(amount) : floorAmount;
    }

    function roundRub(amount) {
        const base = Math.floor(amount / 100) * 100;
        return amount - base > 50 ? base + 100 : base;
    }

    function getPriceSettingKey(city, currency) {
        const cityKey = getCityKey(city);
        const currencyKey = String(currency || "").toLowerCase();

        if (!cityKey || !supportedCurrencies.has(String(currency || ""))) {
            return null;
        }

        return `${cityKey}_${currencyKey}`;
    }

    function loadPriceSettings() {
        if (priceSettings) {
            return Promise.resolve(priceSettings);
        }

        if (!priceSettingsRequest) {
            priceSettingsRequest = fetch(settingsUrl)
                .then(response => response.json())
                .then(result => {
                    if (!result.success) {
                        throw new Error("Could not load document settings");
                    }

                    priceSettings = result.data || {};
                    return priceSettings;
                })
                .catch(error => {
                    priceSettingsRequest = null;
                    throw error;
                });
        }

        return priceSettingsRequest;
    }

    function setCostValue(value) {
        const costInput = document.getElementById("cost");

        if (!costInput) {
            return;
        }

        costInput.value = value === null ? "" : String(value);
    }

    function calculateAutoPrice(settings) {
        const weightInput = document.getElementById("weight");
        const citySelect = document.getElementById("city-select");
        const currency = getSelectedCurrency();
        const settingKey = getPriceSettingKey(citySelect ? citySelect.value : "", currency);

        if (!settingKey) {
            return null;
        }

        const weight = parseNumber(weightInput ? weightInput.value : "");
        const pricePerKg = parseNumber(settings[settingKey]);

        if (weight === null || pricePerKg === null) {
            return null;
        }

        const rawPrice = weight * pricePerKg;

        if (currency === "GEL") {
            return roundGel(rawPrice);
        }

        if (currency === "RUB") {
            return roundRub(rawPrice);
        }

        return null;
    }

    function updateAutoPrice() {
        const autoPriceCheckbox = document.getElementById("autoPrice");

        if (!autoPriceCheckbox || !autoPriceCheckbox.checked) {
            return;
        }

        loadPriceSettings()
            .then(settings => {
                setCostValue(calculateAutoPrice(settings));
            })
            .catch(() => {
                setCostValue(null);
            });
    }

    function bindAutoPrice() {
        const autoPriceCheckbox = document.getElementById("autoPrice");
        const weightInput = document.getElementById("weight");
        const citySelect = document.getElementById("city-select");
        const currencyInputs = document.querySelectorAll("input[name='payment_currency']");

        if (!autoPriceCheckbox) {
            return;
        }

        autoPriceCheckbox.addEventListener("change", function () {
            if (!autoPriceCheckbox.checked) {
                setCostValue(null);
                return;
            }

            updateAutoPrice();
        });

        if (weightInput) {
            weightInput.addEventListener("input", updateAutoPrice);
        }

        if (citySelect) {
            citySelect.addEventListener("change", updateAutoPrice);
        }

        currencyInputs.forEach(input => {
            input.addEventListener("change", updateAutoPrice);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindAutoPrice);
    } else {
        bindAutoPrice();
    }
})();
