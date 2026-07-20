/* Password show/hide toggles + image upload preview. Generic and
   data-attribute driven so it works on any form across the site. */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    // ---- Password show/hide ----
    document.querySelectorAll('.password-toggle-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var targetId = btn.dataset.target;
        var input = document.getElementById(targetId);
        if (!input) return;
        var icon = btn.querySelector('i');
        if (input.type === 'password') {
          input.type = 'text';
          icon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
          input.type = 'password';
          icon.classList.replace('bi-eye-slash', 'bi-eye');
        }
      });
    });

    // ---- Image upload preview ----
    document.querySelectorAll('.image-input-trigger').forEach(function (input) {
      input.addEventListener('change', function () {
        var targetId = input.dataset.previewTarget;
        var preview = document.getElementById(targetId);
        if (!preview || !input.files || !input.files[0]) return;
        var reader = new FileReader();
        reader.onload = function (e) { preview.src = e.target.result; };
        reader.readAsDataURL(input.files[0]);
      });
    });

    // ---- Bootstrap client-side validation feedback ----
    document.querySelectorAll('form[novalidate]').forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      });
    });
  });
})();
