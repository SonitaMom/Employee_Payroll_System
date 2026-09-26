document.addEventListener('DOMContentLoaded', function () {
    const togglePasswordBtn = document.querySelector('#togglePasswordBtn');
    const passwordInput = document.querySelector('#password');
    const toggleIcon = document.querySelector('#toggleIcon');
    const loginForm = document.querySelector('#loginForm');
    const btnSubmit = document.querySelector('#btnSubmit');
    const btnText = document.querySelector('#btnText');
    const btnSpinner = document.querySelector('#btnSpinner');

    // 1. Password Visibility Toggle
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            toggleIcon.classList.toggle('bi-eye', isPassword);
            toggleIcon.classList.toggle('bi-eye-slash', !isPassword);
        });
    }

    // 2. Form Loading State Feedback
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            btnSubmit.disabled = true;
            btnText.textContent = "Signing in...";
            btnSpinner.classList.remove('d-none');
        });
    }
});