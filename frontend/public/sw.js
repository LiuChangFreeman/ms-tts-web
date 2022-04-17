self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('tts').then(cache => cache.addAll([
      '/',
      '/icon.png',
      '/manifest.json',
      '/index.html',
    ])),
  );
});

function isInDissAllowedList(url) {
  const dissAllowedList = ["/tts/generate"];
  for (const item of dissAllowedList) {
    if (url.indexOf(item)!==-1) {
      return true
    }
  }
  return false
}

self.addEventListener('fetch', function (event) {
  event.respondWith(
    caches.match(event.request).then(function (result) {
      const request = event.request;
      const url = request.url;
      if (!isInDissAllowedList(url)) {
        return result || fetch(request).then(response => {
          return caches.open('tts').then(cache => {
            if(request.method==="GET"&&response.status===200) {
              cache.put(request, response.clone());
            }
            return response;
          });
        });
      } else {
        return fetch(request).then(response => {
          return response;
        }).catch(
          async () => {
            if (event.clientId) {
              const client = await clients.get(event.clientId);
              if (client) {
                client.postMessage({
                  msg: "OFFLINE",
                  url: event.request.url
                });
              }
            }
            return result
          }
        );
      }
    }));
});
