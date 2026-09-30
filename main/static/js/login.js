document.addEventListener('DOMContentLoaded', function () {
    const togglePasswordBtn = document.querySelector('#togglePasswordBtn');
    const passwordInput = document.querySelector('#password');
    const toggleIcon = document.querySelector('#toggleIcon');
    const loginForm = document.querySelector('#loginForm');
    const btnSubmit = document.querySelector('#btnSubmit');
    const btnText = document.querySelector('#btnText');
    const btnSpinner = document.querySelector('#btnSpinner');

    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');

            toggleIcon.classList.toggle('bi-eye', isPassword);
            toggleIcon.classList.toggle('bi-eye-slash', !isPassword);
        });
    }

    if (loginForm && btnSubmit && btnText && btnSpinner) {
        const loginFailed = loginForm.dataset.loginError === 'true';

        if (loginFailed) {
            btnSubmit.disabled = false;
            btnText.textContent = 'Try again';
            btnSpinner.classList.add('d-none');
            btnSubmit.removeAttribute('aria-busy');
        }

        loginForm.addEventListener('submit', function () {
            if (!loginForm.checkValidity()) {
                return;
            }

            btnSubmit.disabled = true;
            btnSubmit.setAttribute('aria-busy', 'true');
            btnText.textContent = 'Signing in...';
            btnSpinner.classList.remove('d-none');
        });
    }
});