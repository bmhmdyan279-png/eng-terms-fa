/* Service Worker — Cache-First strategy for the engineering dictionary.
 *
 * - install : precache the app shell
 * - activate: drop old caches
 * - fetch   : serve from cache first; on miss, fetch from network and cache
 *             the response; offline navigations fall back to the cached shell.
 */
"use strict";

var CACHE_NAME = "eng-terms-fa-v2";
var PRECACHE_URLS = [
  "./",
  "./manifest.webmanifest",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",
  // موتور جستجوی ریشه‌محور باید آفلاین هم کار کند — همان وعدهٔ PWA.
  "./assets/js/persian-stem-data.js",
  "./assets/js/persian-stem.js",
  "./assets/js/persian-search.js",
  "./data/api/search-index.json"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then(function (cache) {
        // cache.addAll() کل نصب را شکست می‌دهد اگر حتی یک نشانی ۴۰۴ باشد
        // (مثلاً search-index.json پیش از اجرای build_search_index.py).
        // تک‌تک اضافه می‌کنیم تا یک فایل غایب، PWA را از کار نیندازد.
        return Promise.all(
          PRECACHE_URLS.map(function (url) {
            return cache.add(url).catch(function () {
              /* فایل اختیاری نبود — بی‌صدا رد می‌شویم */
            });
          })
        );
      })
      .then(function () {
        return self.skipWaiting();
      })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches
      .keys()
      .then(function (keys) {
        return Promise.all(
          keys
            .filter(function (key) {
              return key !== CACHE_NAME;
            })
            .map(function (key) {
              return caches.delete(key);
            })
        );
      })
      .then(function () {
        return self.clients.claim();
      })
  );
});

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET") return;

  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) {
        // Cache-First: stale copy wins; refresh the cache in the background.
        event.waitUntil(
          fetch(request)
            .then(function (response) {
              if (response && response.status === 200 && response.type === "basic") {
                var clone = response.clone();
                return caches.open(CACHE_NAME).then(function (cache) {
                  return cache.put(request, clone);
                });
              }
            })
            .catch(function () {
              /* offline refresh — ignore */
            })
        );
        return cached;
      }

      return fetch(request)
        .then(function (response) {
          if (response && response.status === 200 && response.type === "basic") {
            var clone = response.clone();
            event.waitUntil(
              caches.open(CACHE_NAME).then(function (cache) {
                return cache.put(request, clone);
              })
            );
          }
          return response;
        })
        .catch(function () {
          // Offline navigation without a cached page: fall back to the shell.
          if (request.mode === "navigate") {
            return caches.match("./");
          }
          return Response.error();
        });
    })
  );
});
