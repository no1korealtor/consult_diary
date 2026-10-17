const CACHE_NAME = 'consult-diary-v40';

// 기본적으로 캐싱할 에셋 목록 (오프라인에서도 화면을 보여주기 위해)
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
  if (event.request.url.includes('/rosary') || event.request.url.includes('/harmonica')) {
    return; // rosary 및 harmonica 앱은 consult_diary 캐시 대상이 아님
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
