document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const logoutButton = document.getElementById("logout-button");
  const userDetails = document.getElementById("user-details");
  const messageDiv = document.getElementById("message");

  let currentUser = null;

  function showMessage(text, isError = false) {
    if (!messageDiv) return;
    messageDiv.textContent = text;
    messageDiv.className = isError ? "error" : "success";
    messageDiv.classList.remove("hidden");
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function fetchUser() {
    try {
      const response = await fetch("/auth/me");
      if (!response.ok) {
        window.location.href = "index.html";
        return;
      }
      currentUser = await response.json();
      userDetails.innerHTML = `
        <p><strong>${currentUser.name}</strong></p>
        <p>${currentUser.email}</p>
        <p>Branch: ${currentUser.branch}</p>
      `;
    } catch (error) {
      console.error("Failed to load user details:", error);
      window.location.href = "index.html";
    }
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = "<option value=\"\">-- Select an activity --</option>";

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsHTML = details.participants.length > 0
          ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span></li>`
                  )
                  .join("")}
              </ul>
            </div>`
          : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleSignup(event) {
    event.preventDefault();

    if (!currentUser) {
      showMessage("Please login again.", true);
      window.location.href = "index.html";
      return;
    }

    const activity = activitySelect.value;
    if (!activity) {
      showMessage("Please select an activity.", true);
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(currentUser.email)}`,
        {
          method: "POST",
        }
      );
      const result = await response.json();
      if (!response.ok) {
        showMessage(result.detail || "Signup failed", true);
        return;
      }
      showMessage(result.message || "Signup successful");
      fetchActivities();
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", true);
      console.error("Error signing up:", error);
    }
  }

  async function handleLogout() {
    try {
      await fetch("/auth/logout", { method: "POST" });
    } catch (error) {
      console.error("Logout error:", error);
    }
    window.location.href = "index.html";
  }

  if (logoutButton) {
    logoutButton.addEventListener("click", handleLogout);
  }

  if (signupForm) {
    signupForm.addEventListener("submit", handleSignup);
  }

  fetchUser().then(fetchActivities);
});
