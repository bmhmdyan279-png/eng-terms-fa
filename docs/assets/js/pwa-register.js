/* Register the service worker (PWA). Only on https or localhost, so local
 * `mkdocs serve` development without a built index never misbehaves.
 */
(function () {
  "use strict";

  if (!("serviceWorker" in navigator)) return;
  var secure = window.location.protocol === "https:" || window.location.hostname === "localhost";
  if (!secure) return;

  function siteBaseUrl() {
    var bundle = document.querySelector('script[src*="assets/javascripts/bundle"]');
    if (bundle) {
      var idx = bundle.src.indexOf("assets/javascripts/");
      if (idx !== -1) return bundle.src.slice(0, idx);
    }
    return window.location.href.split("#")[0].split("?")[0].replace(/[^/]*$/, "");
  }

  window.addEventListener("load", function () {
    var base = siteBaseUrl();
    navigator.serviceWorker
      .register(base + "sw.js", { scope: base })
      .catch(function () {
        /* SW is progressive enhancement — ignore failures */
      });
  });
})();
