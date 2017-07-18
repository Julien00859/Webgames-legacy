import login from './login.js';
import admin from './admin.js';

class App {
  constructor() {
    this.router();
  }

  router() {
    if (location.pathname === '/admin/login') {
      new login();
    } else if (location.pathname === '/admin') {
      new admin();
    }
  }
}

window.addEventListener('load', _ => new App());
