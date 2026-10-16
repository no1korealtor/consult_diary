const CACHE_NAME = 'rosary-app-v10';
const urlsToCache = [
  '/rosary',
  '/rosary.html',
  '/rosary_icon_192.png',
  '/rosary_icon_512.png',
  '/rosary_manifest.json'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.allSettled(
        urlsToCache.map(url => cache.add(url).catch(e => console.warn('Cache skip:', url, e)))
      );
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
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

// HTML 문서는 무조건 네트워크 우선(Network First)! 오프라인일 때만 캐시 사용!
self.addEventListener('fetch', event => {
  const req = event.request;
  const isHtml = req.mode === 'navigate' || req.destination === 'document' || req.url.includes('/rosary');

  if (isHtml) {
    event.respondWith(
      fetch(req)
        .then(response => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
          }
          return response;
        })
        .catch(() => {
          return caches.match(req).then(cached => cached || caches.match('/rosary.html'));
        })
    );
    return;
  }

  // 아이콘 등 정적 자산은 캐시 우선
  event.respondWith(
    caches.match(req).then(cached => {
      return cached || fetch(req).then(response => {
        if (response && response.status === 200) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
        }
        return response;
      });
    })
  );
});
