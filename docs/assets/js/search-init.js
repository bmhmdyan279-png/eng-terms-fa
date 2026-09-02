/* Pagefind integration for Material for MkDocs.
 *
 * Pagefind's index and UI assets are generated into site/pagefind/ by CI
 * (npx pagefind --site site/) AFTER mkdocs build, so they are loaded
 * dynamically at runtime. The site base path is derived from Material's
 * own bundle script so this works on project pages (e.g. /eng-terms-fa/).
 */
(function () {
  "use strict";

  function siteBaseUrl() {
    var bundle = document.querySelector('script[src*="assets/javascripts/bundle"]');
    if (bundle) {
      var idx = bundle.src.indexOf("assets/javascripts/");
      if (idx !== -1) return bundle.src.slice(0, idx);
    }
    return window.location.href.split("#")[0].split("?")[0].replace(/[^/]*$/, "");
  }

  function loadAsset(kind, url) {
    return new Promise(function (resolve, reject) {
      if (kind === "css") {
        var link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = url;
        link.onload = resolve;
        link.onerror = reject;
        document.head.appendChild(link);
      } else {
        var script = document.createElement("script");
        script.src = url;
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
      }
    });
  }

  function mountUi(target) {
    /* eslint-disable-next-line no-undef */
    new PagefindUI({
      element: target,
      showSubResults: true,
      showImages: false,
      translations: {
        placeholder: "جستجوی واژه…",
        clear_search: "پاک کردن",
        load_more: "نتایج بیشتر",
        search_label: "جستجو",
        zero_results: "نتیجه‌ای یافت نشد"
      }
    });
  }

  function fallback(target) {
    target.innerHTML =
      '<p>نمایهٔ جستجوی Pagefind در دسترس نیست (در اجرای محلی، پس از ' +
      "<code>mkdocs build</code> دستور <code>npx pagefind --site site/</code> را اجرا کنید). " +
      "می‌توانید از جستجوی پیش‌فرض بالای صفحه استفاده کنید.</p>";
  }

  function init() {
    var target = document.getElementById("pagefind-ui");
    if (!target || target.dataset.pagefindInit === "done") return;
    target.dataset.pagefindInit = "done";

    var base = siteBaseUrl();
    loadAsset("css", base + "pagefind/pagefind-ui.css")
      .then(function () {
        return loadAsset("js", base + "pagefind/pagefind-ui.js");
      })
      .then(function () {
        if (typeof window.PagefindUI === "undefined") {
          fallback(target);
          return;
        }
        mountUi(target);
      })
      .catch(function () {
        fallback(target);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
