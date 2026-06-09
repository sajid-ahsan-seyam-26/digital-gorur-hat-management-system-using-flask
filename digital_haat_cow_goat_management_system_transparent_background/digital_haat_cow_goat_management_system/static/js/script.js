// ------------------------------------------------------------
// Digital Haat Cow & Goat Management System
// Beginner friendly JavaScript
// ------------------------------------------------------------

function updateLiveClock() {
    const clockElement = document.getElementById("liveClock");

    if (clockElement !== null) {
        const now = new Date();
        const timeText = now.toLocaleTimeString();
        clockElement.textContent = timeText;
    }
}

function setupSidebarButton() {
    const menuButton = document.getElementById("menuButton");
    const sidebar = document.getElementById("sidebar");

    if (menuButton !== null && sidebar !== null) {
        menuButton.addEventListener("click", function () {
            sidebar.classList.toggle("open-sidebar");
        });
    }
}

function setupDeleteConfirmation() {
    const deleteForms = document.querySelectorAll(".delete-form");

    deleteForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const confirmed = confirm("Are you sure you want to delete this animal profile? This will also delete related health, feeding and sale records.");

            if (confirmed === false) {
                event.preventDefault();
            }
        });
    });
}

function setupAutoAlertClose() {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alertBox) {
        setTimeout(function () {
            alertBox.style.opacity = "0";
            alertBox.style.transform = "translateY(-8px)";
            alertBox.style.transition = "0.4s ease";
        }, 3500);
    });
}

function setupSalePriceMessage() {
    const salePriceInput = document.getElementById("salePrice");

    if (salePriceInput !== null) {
        salePriceInput.addEventListener("input", function () {
            const value = Number(salePriceInput.value);

            if (value > 0) {
                salePriceInput.title = "Sale price entered: ৳ " + value.toFixed(2);
            }
        });
    }
}

updateLiveClock();
setInterval(updateLiveClock, 1000);
setupSidebarButton();
setupDeleteConfirmation();
setupAutoAlertClose();
setupSalePriceMessage();
