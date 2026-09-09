/* Faceted filters for the generated term index (docs/terms/index.md).
 *
 * Each <li class="term-row"> carries:
 *   data-domain  : space separated domain ids (e.g. "construction materials")
 *   data-status  : draft | reviewed | published
 *   data-langs   : space separated available language codes (e.g. "en fr de")
 *   data-fa      : Persian term (sort key)
 *   data-en      : English equivalent (alternate sort key)
 *
 * The filter state is mirrored into the URL (?domain=…&status=…&langs=…&sort=…)
 * so a filtered view can be shared as a link and survives reload/back.
 */
(function () {
  "use strict";

  var faCollator = typeof Intl !== "undefined" ? new Intl.Collator("fa") : null;
  var enCollator = typeof Intl !== "undefined" ? new Intl.Collator("en") : null;

  var PARAM_OF = {
    domain: "filter-domain",
    status: "filter-status",
    langs: "filter-langs",
    sort: "filter-sort"
  };

  function init() {
    var list = document.getElementById("terms-list");
    if (!list || list.dataset.filtersInit === "done") return;
    list.dataset.filtersInit = "done";

    var domainSelect = document.getElementById("filter-domain");
    var statusSelect = document.getElementById("filter-status");
    var langsSelect = document.getElementById("filter-langs");
    var sortSelect = document.getElementById("filter-sort");
    var counter = document.getElementById("terms-count");
    var selects = {
      domain: domainSelect,
      status: statusSelect,
      langs: langsSelect,
      sort: sortSelect
    };

    var rows = Array.prototype.slice.call(list.querySelectorAll("li.term-row"));

    // --- restore filter state from the URL (shared links / reload / back) ---
    function readURL() {
      if (typeof URLSearchParams === "undefined" || !window.location.search) return;
      var params = new URLSearchParams(window.location.search);
      Object.keys(PARAM_OF).forEach(function (key) {
        var el = selects[key];
        var value = params.get(key);
        if (el && value !== null) {
          // only accept values that exist as options (ignore junk in the URL)
          for (var i = 0; i < el.options.length; i++) {
            if (el.options[i].value === value) { el.value = value; break; }
          }
        }
      });
    }

    function writeURL() {
      if (typeof URLSearchParams === "undefined" || !window.history || !window.history.replaceState) return;
      var params = new URLSearchParams();
      Object.keys(PARAM_OF).forEach(function (key) {
        var el = selects[key];
        if (el && el.value) params.set(key, el.value);
      });
      var query = params.toString();
      var url = window.location.pathname + (query ? "?" + query : "") + window.location.hash;
      window.history.replaceState(null, "", url);
    }

    function apply() {
      var domain = domainSelect ? domainSelect.value : "";
      var status = statusSelect ? statusSelect.value : "";
      var langs = langsSelect ? langsSelect.value : "";
      var sortKey = sortSelect ? sortSelect.value : "fa";
      var visible = 0;

      rows.forEach(function (row) {
        var domains = (row.dataset.domain || "").split(/\s+/);
        var langsAvail = (row.dataset.langs || "").split(/\s+/);
        var show = true;
        if (domain && domains.indexOf(domain) === -1) show = false;
        if (status && row.dataset.status !== status) show = false;
        if (langs && langsAvail.indexOf(langs) === -1) show = false;
        row.style.display = show ? "" : "none";
        if (show) visible++;
      });

      var collator = sortKey === "en" ? enCollator : faCollator;
      var attr = sortKey === "en" ? "data-en" : "data-fa";
      var sorted = rows.slice().sort(function (a, b) {
        var av = a.getAttribute(attr) || "";
        var bv = b.getAttribute(attr) || "";
        if (collator) return collator.compare(av, bv);
        return av < bv ? -1 : av > bv ? 1 : 0;
      });
      sorted.forEach(function (row) {
        list.appendChild(row);
      });

      if (counter) {
        counter.textContent = "نمایش " + toFaDigits(visible) + " از " + toFaDigits(rows.length) + " واژه";
      }

      writeURL();
    }

    function toFaDigits(n) {
      return String(n).replace(/\d/g, function (d) {
        return "۰۱۲۳۴۵۶۷۸۹"[d];
      });
    }

    [domainSelect, statusSelect, langsSelect, sortSelect].forEach(function (el) {
      if (el) el.addEventListener("change", apply);
    });

    readURL();
    apply();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
