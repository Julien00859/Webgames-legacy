const cache = [
  '/admin/',
  '/admin/login',
  '/admin/static/app.js',
  '/admin/static/style.css'
];

self.oninstall = event => {

}

self.onactivate = event => {

}

self.onfetch = event => {
  fetch(event.request);
}
