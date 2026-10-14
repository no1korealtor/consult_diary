const CACHE_NAME = 'rosary-app-v2';
const urlsToCache = [
  './rosary.html',
  './rosary_icon_192.png',
  './rosary_icon_512.png',
  './rosary_manifest.json'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(k => {
          if (k.startsWith('rosary-app-') && k !== CACHE_NAME) {
            return caches.delete(k);
          }
        })
      );
    })
  );
});
