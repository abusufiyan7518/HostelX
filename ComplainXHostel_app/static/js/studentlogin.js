function togglePassword(id, iconId) {
  const passwordInput = document.getElementById(id);
  const icon = document.getElementById(iconId);

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    icon.classList.replace("fa-eye", "fa-eye-slash");
  } else {
    passwordInput.type = "password";
    icon.classList.replace("fa-eye-slash", "fa-eye");
  }
}

// Form validation
document.getElementById("loginForm").addEventListener("submit", function (event) {
  event.preventDefault(); // Stop default reload

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (email === "" || password === "") {
    alert("Please fill in all fields!");
    return;
  }

  //  SET USER ROLE - ADD THIS LINE
  localStorage.setItem("userRole", "user");
  
  // Set current user data for profile page
  // Try to get user from localStorage users list, or create basic user data
  let users = JSON.parse(localStorage.getItem('users') || '[]');
  let userData = users.find(u => u.email === email && u.type === 'user');
  
  if (!userData) {
    // If user not found in registration list, create basic data
    userData = {
      name: email.split('@')[0], // Use email prefix as name
      email: email,
      mobile: '', // Will be empty if not provided during login
      type: 'user',
      registeredAt: new Date().toISOString()
    };
  }
  
  localStorage.setItem("currentUser", JSON.stringify(userData));
  localStorage.setItem("isLoggedIn", "true");

  // Simulate successful login
  alert("Login successful!");
  window.location.href = "/home/";  // this hits views.home → index.html
});