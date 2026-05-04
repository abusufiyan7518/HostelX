
// Toggle password visibility
function togglePassword(inputId, iconId) {
  const passwordInput = document.getElementById(inputId);
  const eyeIcon = document.getElementById(iconId);
  
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    eyeIcon.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
    passwordInput.type = 'password';
    eyeIcon.classList.replace('fa-eye-slash', 'fa-eye');
  }
}

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
  const registerForm = document.getElementById('registerForm');
  
  if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const name = document.getElementById('name').value.trim();
      const mobile = document.getElementById('Mobile').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirmPassword').value;
      
      //  Basic validation
      if (password !== confirmPassword) {
        alert(' Passwords do not match!');
        return;
      }

      if (password.length < 6) {
        alert(' Password must be at least 6 characters long!');
        return;
      }

      if (mobile.length !== 10) {
        alert(' Mobile number must be 10 digits!');
        return;
      }

    
      const user = {
        name,
        mobile,
        email,
        password,
        type: 'user', // identifies as regular user
        registeredAt: new Date().toISOString()
      };

      //  Get existing users and add new one (no duplicate checks)
      let users = JSON.parse(localStorage.getItem('users') || '[]');
      users.push(user);
      localStorage.setItem('users', JSON.stringify(users));

      //  Set current user as logged in
      localStorage.setItem('currentUser', JSON.stringify(user));
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userRole', 'user');

      //  Success message
      alert(' Registration successful! Redirecting to login page...');
      registerForm.reset();

      //  Redirect to home
      setTimeout(() => {
        window.location.href = '/Student_login/';
      }, 1000);
    });
  }
});


// Optional: Password match live validation
document.addEventListener('DOMContentLoaded', function() {
  const password = document.getElementById('password');
  const confirmPassword = document.getElementById('confirmPassword');
  
  if (confirmPassword) {
    confirmPassword.addEventListener('input', function() {
      confirmPassword.setCustomValidity(
        password.value !== confirmPassword.value ? 'Passwords do not match' : ''
      );
    });
  }
});
