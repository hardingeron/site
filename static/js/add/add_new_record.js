document.querySelector("form").addEventListener("submit", function (event) {
    event.preventDefault();

    const saveButton = document.querySelector("button[type='submit']");
    saveButton.disabled = true;
    saveButton.style.opacity = "0.5";

    setTimeout(function () {
        saveButton.disabled = false;
        saveButton.style.opacity = "1";
    }, 2000);

    const requiredFields = [
        { input: document.querySelector("input[name='sender']"), error: "sender" },
        { input: document.querySelector("input[name='sender_phone']"), error: "sender_phone" },
        { input: document.querySelector("input[name='recipient']"), error: "recipient" },
        { input: document.querySelector("input[name='recipient_phone']"), error: "recipient_phone" },
        { input: document.querySelector("textarea[name='inventory']"), error: "inventory" },
        { input: document.querySelector("input[name='weight']"), error: "weight" },
        { input: document.querySelector("input[name='cost']"), error: "cost" },
        { input: document.querySelector("select[name='city']"), error: "city" },
        { input: document.querySelector("input[name='payment']:checked"), error: "payment" },
        { input: document.querySelector("input[name='payment_currency']:checked"), error: "payment_currency" }
    ];

    let isValid = true;

    for (const { input } of requiredFields) {
        const value = input ? input.value.trim() : "";

        if (value === "") {
            isValid = false;
            if (input) {
                input.style.border = "1px solid red";
                setTimeout(() => {
                    input.style.border = "1px solid #9c9c9c7a";
                }, 2000);
            }
        }
    }

    if (!isValid) {
        Swal.fire({
            icon: "error",
            title: "შეცდომა!",
            text: "შეავსეთ აუცილებელი ველები!"
        });
        return;
    }

    const formData = new FormData();

    formData.append("sender", document.querySelector("input[name='sender']").value);
    formData.append("sender_phone", document.querySelector("input[name='sender_phone']").value);
    formData.append("recipient", document.querySelector("input[name='recipient']").value);
    formData.append("recipient_phone", document.querySelector("input[name='recipient_phone']").value);
    formData.append("inventory", document.querySelector("textarea[name='inventory']").value);
    formData.append("weight", document.querySelector("input[name='weight']").value);
    formData.append("responsibility", document.querySelector("input[name='responsibility']").value);
    formData.append("passport", document.querySelector("input[name='passport']").value);
    formData.append("cost", document.querySelector("input[name='cost']").value);
    formData.append("city", document.querySelector("select[name='city']").value);

    const paymentMethod = document.querySelector("input[name='payment']:checked");
    if (paymentMethod) {
        formData.append("payment", paymentMethod.value);
    }

    const paymentCurrency = document.querySelector("input[name='payment_currency']:checked");
    if (paymentCurrency) {
        formData.append("payment_currency", paymentCurrency.value);
    }

    const photoInput = document.getElementById("photo");
    const photoFile = photoInput.files[0];
    if (photoFile) {
        formData.append("photo", photoFile);
    }

    const currentDate = new Date();
    const departureStatus = document.getElementById("departureStatus").checked;
    formData.append("departureStatus", departureStatus ? "selected" : "not selected");

    function addLeadingZero(number) {
        return number < 10 ? "0" + number : number;
    }

    const formattedDate = addLeadingZero(currentDate.getDate()) + "." +
        addLeadingZero(currentDate.getMonth() + 1) + "." +
        currentDate.getFullYear() + " " +
        addLeadingZero(currentDate.getHours()) + ":" +
        addLeadingZero(currentDate.getMinutes()) + ":" +
        addLeadingZero(currentDate.getSeconds());

    formData.append("currentDateTime", formattedDate);

    fetch("/saving_a_parcel", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: "vipost:parcel-created",
                        message: data.message
                    }, window.location.origin);
                }

                Swal.fire({
                    icon: "success",
                    title: "წარმატება!",
                    text: data.message,
                    showConfirmButton: false,
                    timer: 5000
                });

                document.querySelector("input[name='sender']").value = "";
                document.querySelector("input[name='sender_phone']").value = "";
                document.querySelector("input[name='recipient']").value = "";
                document.querySelector("input[name='recipient_phone']").value = "";
                document.querySelector("textarea[name='inventory']").value = "";
                document.querySelector("input[name='weight']").value = "";
                document.querySelector("input[name='responsibility']").value = "";
                document.querySelector("input[name='passport']").value = "";
                document.querySelector("input[name='cost']").value = "";
                document.querySelector("select[name='city']").value = "";

                const selectedPayment = document.querySelector("input[name='payment']:checked");
                if (selectedPayment) {
                    selectedPayment.checked = false;
                }

                const selectedCurrency = document.querySelector("input[name='payment_currency']:checked");
                if (selectedCurrency) {
                    selectedCurrency.checked = false;
                }

                document.getElementById("photo").value = "";
                document.getElementById("departureStatus").checked = false;

                const autoPriceCheckbox = document.getElementById("autoPrice");
                if (autoPriceCheckbox) {
                    autoPriceCheckbox.checked = false;
                }
            } else {
                Swal.fire({
                    icon: "error",
                    title: "შეცდომა!",
                    text: data.message || "ამანათის შენახვა ვერ მოხერხდა."
                });
            }
        })
        .catch(() => {
            Swal.fire({
                icon: "error",
                title: "შეცდომა!",
                text: "სერვერთან კავშირი ვერ მოხერხდა."
            });
        });
});
