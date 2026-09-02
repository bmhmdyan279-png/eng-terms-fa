/* واژهٔ روز — rotates daily on the client so a static site still shows a
 * new term every day. The server renders a build-time fallback inside
 * #totd; this script replaces it with today's deterministic pick.
 */
(function () {
  "use strict";

  function seeded(seed) {
    var s = seed >>> 0;
    s = Math.imul(s ^ (s >>> 15), s | 1);
    s ^= s + Math.imul(s ^ (s >>> 7), s | 61);
    return ((s ^ (s >>> 14)) >>> 0) / 4294967296;
  }

  function esc(text) {
    var div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
  }

  function render(term) {
    var def = term[3] || "";
    if (def.length > 140) def = def.slice(0, 140) + "…";
    return (
      '<div class="totd-card">' +
      '<span class="totd-label">واژهٔ روز</span>' +
      '<a class="totd-term" href="terms/' + esc(term[0]) + '/">' + esc(term[1]) + "</a>" +
      '<span class="totd-en" dir="ltr" lang="en">' + esc(term[2]) + "</span>" +
      '<p class="totd-def">' + esc(def) + "</p>" +
      "</div>"
    );
  }

  function init() {
    var host = document.getElementById("totd");
    var dataEl = document.getElementById("totd-data");
    if (!host || !dataEl || host.dataset.totdInit === "done") return;
    host.dataset.totdInit = "done";

    var list;
    try {
      list = JSON.parse(dataEl.textContent);
    } catch (e) {
      return;
    }
    if (!Array.isArray(list) || list.length === 0) return;

    var now = new Date();
    var seed = now.getFullYear() * 10000 + (now.getMonth() + 1) * 100 + now.getDate();
    var index = Math.floor(seeded(seed) * list.length);
    host.innerHTML = render(list[index]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
