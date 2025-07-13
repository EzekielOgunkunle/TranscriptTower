self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open('transcript-tower-v1').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/custom_bootstrap.css',
        '/static/manifest.webmanifest',
        // Add more static assets as needed
      ]);
    })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});
