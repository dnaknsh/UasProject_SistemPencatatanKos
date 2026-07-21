// Validasi sisi client menggunakan Bootstrap validation API.
// Mencegah form dikirim jika ada input yang kosong / tidak valid,
// sebagai lapisan pertama sebelum validasi ulang dilakukan di sisi server (app.py).
(function () {
    "use strict";

    const forms = document.querySelectorAll("form.needs-validation");

    Array.from(forms).forEach((form) => {
        form.addEventListener(
            "submit",
            (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add("was-validated");
            },
            false
        );
    });

    // Auto-dismiss alert setelah beberapa detik
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alertEl) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });
})();