// Service Worker for Automotive History Trivia
const CACHE_NAME = 'automotive-trivia-v1.0.1';
const RUNTIME_CACHE = 'automotive-trivia-runtime';

// Files to cache immediately
const PRECACHE_ASSETS = [
  './',
  './index.html',
  './game.css',
  './game.js',
  './game.json',
  './manifest.json',
  './media/graphics/promo/icons/128x128.png',
  './media/graphics/loading/ajax-loader.gif',
  './media/graphics/orientate/portrait.png',
  './media/graphics/backgrounds/desktop/cover.png',
  './media/graphics/sprites/title.png',
  './media/graphics/splash/loading_frame.png',
  './media/graphics/splash/loading_bar.png',
  './media/text/lato-black.ttf',
  './media/text/lato-regular.ttf'
];

// Install event - cache essential files
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching essential files');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }

  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        return fetch(request).then((networkResponse) => {
          // Cache successful responses
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(RUNTIME_CACHE).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return networkResponse;
        });
      })
      .catch(() => {
        // Return offline page or fallback
        if (request.destination === 'document') {
          return caches.match('./index.html');
        }
      })
  );
});

// Message event - allow manual cache updates
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
