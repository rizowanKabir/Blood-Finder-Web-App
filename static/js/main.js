/* Sticky navbar shadow, back-to-top button, scroll-reveal animations,
   page loader fade-out, and auto-dismissing toast notifications. */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    // ---- Page loader ----
    var loader = document.getElementById('page-loader');
    if (loader) {
      window.addEventListener('load', function () {
        loader.classList.add('loaded');
      });
      // Safety net in case 'load' already fired or is slow to fire
      setTimeout(function () { loader.classList.add('loaded'); }, 1200);
    }

    // ---- Sticky navbar shadow on scroll ----
    var navbar = document.getElementById('mainNavbar');
    function handleNavbarScroll() {
      if (!navbar) return;
      navbar.classList.toggle('scrolled', window.scrollY > 12);
    }
    handleNavbarScroll();
    window.addEventListener('scroll', handleNavbarScroll, { passive: true });

    // ---- Back to top ----
    var backToTop = document.getElementById('back-to-top');
    if (backToTop) {
      window.addEventListener('scroll', function () {
        backToTop.classList.toggle('show', window.scrollY > 400);
      }, { passive: true });
      backToTop.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // ---- Scroll-reveal animations ----
    var revealTargets = document.querySelectorAll('.fade-in-up');
    if ('IntersectionObserver' in window && revealTargets.length) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12 });
      revealTargets.forEach(function (el) { observer.observe(el); });
    } else {
      revealTargets.forEach(function (el) { el.classList.add('in-view'); });
    }

    // ---- Toasts: auto-dismiss after data-autohide ms ----
    document.querySelectorAll('.toast-alert').forEach(function (toast) {
      var delay = parseInt(toast.dataset.autohide, 10) || 6000;
      setTimeout(function () {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', function () { toast.remove(); }, { once: true });
        toast.style.opacity = '0';
      }, delay);
    });
  });
})();
