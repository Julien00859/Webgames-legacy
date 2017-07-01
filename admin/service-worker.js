const name = 'wg-admin';
const version = '1.0';

const static = [
  '/admin/login',
  '/admin/static/admin.js',
  '/admin/static/login.js',
  '/admin/static/style.css'
];

self.oninstall = event => {
  event.waitUntil(
    caches.open(`${name}-${version}`)
      .then(cache => cache.addAll(static))
      .catch(error => console.error(error))
  );
}

self.onactivate = event => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
          .map(cacheName => cacheName.split('-'))
          .filter(cacheName => cacheName[0] + '-' + cacheName[1] !== name)
          .filter(cacheName => cacheName[2] !== version)
          .map(cacheName => caches.delete(cacheName.join('-')))
        );
      })
  );
}

self.onfetch = event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(error => console.error(error))
  );
}
