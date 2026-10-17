const CACHE_NAME = 'consult-diary-v39';

// 湲곕낯?곸쑝濡?罹먯떛???먯뀑 紐⑸줉 (?ㅽ봽?쇱씤?먯꽌???붾㈃??蹂댁뿬二쇨린 ?꾪빐)
const urlsToCache = [
  './login.html',
  './app.css',
  './icon.png',
  './manifest.json'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  if (event.request.url.includes('/rosary')) {
    return; // rosary 앱은 consult_diary 캐시 대상이 아님
  }
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
