document.addEventListener("DOMContentLoaded", () => {

    // ===========================
    // Mobile Navigation
    // ===========================

    const navToggle = document.getElementById("navToggle");
    const navLinks = document.getElementById("navLinks");

    if (navToggle && navLinks) {

        navToggle.addEventListener("click", () => {

            navLinks.classList.toggle("active");

            const expanded =
                navLinks.classList.contains("active");

            navToggle.setAttribute(
                "aria-expanded",
                expanded
            );

        });

        navLinks.querySelectorAll("a").forEach((link) => {

            link.addEventListener("click", () => {

                navLinks.classList.remove("active");

                navToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            });

        });

    }


    // ===========================
    // Close Alert Button
    // ===========================

    const closeButtons =
        document.querySelectorAll(".alert-close");

    closeButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const alert =
                button.closest(".alert");

            if (!alert) return;

            alert.style.transition =
                "all 0.3s ease";

            alert.style.opacity = "0";
            alert.style.transform =
                "translateX(20px)";

            setTimeout(() => {

                alert.remove();

            }, 300);

        });

    });


    // ===========================
    // Auto Hide Messages
    // ===========================

    const alerts =
        document.querySelectorAll(".alert");

    alerts.forEach((alert) => {

        setTimeout(() => {

            alert.style.transition =
                "all 0.3s ease";

            alert.style.opacity = "0";
            alert.style.transform =
                "translateX(20px)";

            setTimeout(() => {

                alert.remove();

            }, 300);

        }, 5000);

    });

});