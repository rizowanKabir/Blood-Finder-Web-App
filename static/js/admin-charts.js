/* Renders the three Chart.js charts on the staff-only admin stats
   dashboard, fed by dashboard:admin_stats_api. Colors match the
   pink/cyan theme instead of Chart.js defaults. */
(function () {
  'use strict';

  var PINK = '#FF4F8B', CYAN = '#00D9FF', CYAN_DARK = '#0099CC', PINK_LIGHT = '#FFD6E7', GREY = '#94A3B8';

  document.addEventListener('DOMContentLoaded', function () {
    var bloodGroupCanvas = document.getElementById('chartBloodGroup');
    if (!bloodGroupCanvas || typeof Chart === 'undefined') return;

    fetch('/dashboard/admin-stats/api/')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        new Chart(bloodGroupCanvas, {
          type: 'doughnut',
          data: {
            labels: data.donors_by_group.map(function (d) { return d.blood_group; }),
            datasets: [{
              data: data.donors_by_group.map(function (d) { return d.count; }),
              backgroundColor: [PINK, CYAN, CYAN_DARK, PINK_LIGHT, '#FB923C', '#A78BFA', '#34D399', '#F472B6'],
              borderWidth: 0,
            }],
          },
          options: { plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } } },
        });

        new Chart(document.getElementById('chartStatus'), {
          type: 'bar',
          data: {
            labels: data.requests_by_status.map(function (d) { return d.status; }),
            datasets: [{
              data: data.requests_by_status.map(function (d) { return d.count; }),
              backgroundColor: [PINK, CYAN_DARK, GREY],
              borderRadius: 8,
            }],
          },
          options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
        });

        new Chart(document.getElementById('chartMonthly'), {
          type: 'line',
          data: {
            labels: data.requests_by_month.map(function (d) { return d.month; }),
            datasets: [{
              label: 'Requests',
              data: data.requests_by_month.map(function (d) { return d.count; }),
              borderColor: PINK,
              backgroundColor: 'rgba(255,79,139,0.15)',
              fill: true,
              tension: 0.35,
            }],
          },
          options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
        });
      })
      .catch(function (err) { console.error('Failed to load admin stats', err); });
  });
})();
