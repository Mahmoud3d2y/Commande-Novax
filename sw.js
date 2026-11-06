// Cache hors ligne. Changer VERSION à chaque mise à jour du tarif.
const VERSION = "novax-v2";
const FILES = ["./", "./index.html", "./manifest.webmanifest", "./icons/icon.svg", "./icons/icon-192.png", "./icons/icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== VERSION).map(x => caches.delete(x)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  // Page : réseau d'abord (mises à jour du tarif visibles tout de suite), cache si hors ligne.
  if (e.request.mode === "navigate") {
    e.respondWith(fetch(e.request).then(res => {
      const cp = res.clone(); caches.open(VERSION).then(c => c.put("./index.html", cp)); return res;
    }).catch(() => caches.match("./index.html")));
    return;
  }
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(r => r || fetch(e.request).then(res => {
    if (res.ok && new URL(e.request.url).origin === location.origin) { const cp = res.clone(); caches.open(VERSION).then(c => c.put(e.request, cp)); }
    return res;
  })));
});
