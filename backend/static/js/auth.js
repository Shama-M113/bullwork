document.addEventListener("DOMContentLoaded", function () {
    console.log("Auth JS Loaded");

    const form = document.getElementById("loginForm");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        document.getElementById("error").innerText = "";

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const res = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (res.ok) {
                // Store JWT token in localStorage
                localStorage.setItem("token", data.access_token);

                // Redirect based on role
                if (data.role === "admin") {
                    window.location.href = "/admin";  // matches Flask route
                } else {
                    window.location.href = "/user";   // matches Flask route
                }
            } else {
                document.getElementById("error").innerText = data.message;
            }
        } catch (err) {
            console.error("Login error:", err);
            document.getElementById("error").innerText = "Something went wrong";
        }
    });
});
