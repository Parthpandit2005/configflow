document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("theme-toggle");

    if (!themeToggle) {
        return;
    }

    const savedTheme = localStorage.getItem("testpro-theme");

    if (savedTheme === "light") {
        document.body.classList.add("light-mode");
        themeToggle.textContent = "☾";
    } else {
        themeToggle.textContent = "☀";
    }


    themeToggle.addEventListener("click", function () {

        document.body.classList.toggle("light-mode");

        const isLight =
            document.body.classList.contains("light-mode");

        localStorage.setItem(
            "testpro-theme",
            isLight ? "light" : "dark"
        );

        themeToggle.textContent =
            isLight ? "☾" : "☀";

    });

});