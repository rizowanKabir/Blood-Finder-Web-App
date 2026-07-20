/* Instant donor search preview on the homepage hero widget. Debounces
   field changes and calls the lightweight JSON search-api endpoint,
   rendering a live preview without leaving the page. Submitting the
   form still does a full server-rendered search (robust + paginated). */
(function () {
  'use strict';

  function debounce(fn, wait) {
    var timer;
    return function () {
      var args = arguments, ctx = this;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(ctx, args); }, wait);
    };
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('heroSearchForm');
    var resultsBox = document.getElementById('instantResultsPreview');
    if (!form || !resultsBox) return;

    var apiUrl = form.dataset.searchApiUrl;

    function renderResults(data) {
      if (!data.results || !data.results.length) {
        resultsBox.innerHTML = '<div class="text-muted small px-2">No matching donors yet — try different filters, or widen your search.</div>';
        return;
      }
      var html = data.results.map(function (donor) {
        return '<a class="instant-results-item" href="' + donor.url + '">' +
          '<span>' + donor.name + ' — ' + donor.blood_group + '</span>' +
          '<span class="text-muted">' + donor.district + ', ' + donor.division + '</span></a>';
      }).join('');
      if (data.total > data.results.length) {
        html += '<div class="text-muted small px-2 mt-1">+ ' + (data.total - data.results.length) + ' more — press Search to see all</div>';
      }
      resultsBox.innerHTML = html;
    }

    var runSearch = debounce(function () {
      var params = new URLSearchParams(new FormData(form));
      fetch(apiUrl + '?' + params.toString())
        .then(function (res) { return res.ok ? res.json() : Promise.reject(res.status); })
        .then(renderResults)
        .catch(function () { resultsBox.innerHTML = ''; });
    }, 350);

    form.querySelectorAll('select, input').forEach(function (field) {
      field.addEventListener('input', runSearch);
      field.addEventListener('change', runSearch);
    });
  });
})();
