document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(text, isError = false) {
    if (!messageDiv) return;
    messageDiv.textContent = text;
    messageDiv.className = isError ? "error" : "success";
    messageDiv.classList.remove("hidden");
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function handleLogin(event) {
    event.preventDefault();

    const formData = new FormData(loginForm);

    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (!response.ok) {
        showMessage(result.detail || "Login failed", true);
        return;
      }

      showMessage(result.message || "Login successful");
      window.location.href = "portal.html";
    } catch (error) {
      showMessage("Unable to complete login. Try again.", true);
      console.error("Login error:", error);
    }
  }

  async function handleSignup(event) {
    event.preventDefault();

    const formData = new FormData(signupForm);

    try {
      const response = await fetch("/auth/signup", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (!response.ok) {
        showMessage(result.detail || "Signup failed", true);
        return;
      }

      showMessage(result.message || "Signup successful");
      setTimeout(() => {
        window.location.href = "index.html";
      }, 1200);
    } catch (error) {
      showMessage("Unable to complete signup. Try again.", true);
      console.error("Signup error:", error);
    }
  }

  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
  }

  if (signupForm) {
    signupForm.addEventListener("submit", handleSignup);
  }
});
