'use strict';

class Toast {
  static Push(message, options = { duration: 3000 }) {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    const toastContent = document.createElement('p');
    toast.classList.add('toast');
    toastContent.classList.add('toast-content');
    toastContent.textContent = message;
    container.appendChild(toast);
    toast.appendChild(toastContent);
    setTimeout(() => toast.classList.add('hide'), options.duration);
    toast.addEventListener('transitionend', evt => evt.target.parentNode.removeChild(evt.target));
  }
}

function createCommonjsModule(fn, module) {
	return module = { exports: {} }, fn(module, module.exports), module.exports;
}

var idbKeyval = createCommonjsModule(function (module) {
(function() {
  'use strict';
  var db;
  function getDB() {
    if (!db) {
      db = new Promise(function(resolve, reject) {
        var openreq = indexedDB.open('keyval-store', 1);
        openreq.onerror = function() {
          reject(openreq.error);
        };
        openreq.onupgradeneeded = function() {
          openreq.result.createObjectStore('keyval');
        };
        openreq.onsuccess = function() {
          resolve(openreq.result);
        };
      });
    }
    return db;
  }
  function withStore(type, callback) {
    return getDB().then(function(db) {
      return new Promise(function(resolve, reject) {
        var transaction = db.transaction('keyval', type);
        transaction.oncomplete = function() {
          resolve();
        };
        transaction.onerror = function() {
          reject(transaction.error);
        };
        callback(transaction.objectStore('keyval'));
      });
    });
  }
  var idbKeyval = {
    get: function(key) {
      var req;
      return withStore('readonly', function(store) {
        req = store.get(key);
      }).then(function() {
        return req.result;
      });
    },
    set: function(key, value) {
      return withStore('readwrite', function(store) {
        store.put(value, key);
      });
    },
    delete: function(key) {
      return withStore('readwrite', function(store) {
        store.delete(key);
      });
    },
    clear: function() {
      return withStore('readwrite', function(store) {
        store.clear();
      });
    },
    keys: function() {
      var keys = [];
      return withStore('readonly', function(store) {
        (store.openKeyCursor || store.openCursor).call(store).onsuccess = function() {
          if (!this.result) return;
          keys.push(this.result.key);
          this.result.continue();
        };
      }).then(function() {
        return keys;
      });
    }
  };
  if ('object' != 'undefined' && module.exports) {
    module.exports = idbKeyval;
  } else if (typeof undefined === 'function' && undefined.amd) {
    undefined('idbKeyval', [], function() {
      return idbKeyval;
    });
  } else {
    self.idbKeyval = idbKeyval;
  }
}());
});

class Login {
  constructor() {
    this.form = document.querySelector('.login-form');
    this.loginAdmin = this.loginAdmin.bind(this);
    this.addEventListeners();
  }
  loginAdmin(evt) {
    evt.preventDefault();
    const username = evt.target.username.value;
    const password = evt.target.password.value;
    fetch('/auth/login/admin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        password
      })
    }).then(response => response.json()).then(response => {
      if (response.error) {
        Toast.Push(response.error);
        return;
      }
      Toast.Push(response.success, { duration: 15000 });
      this.saveToken(response.token);
    }).catch(error => console.error(error));
  }
  async saveToken(token) {
    await idbKeyval.set('token', token);
  }
  addEventListeners() {
    this.form.addEventListener('submit', this.loginAdmin);
  }
}

class Admin {
  constructor() {
    this.gamesUpdate = Array.from(document.querySelectorAll('.game-form'));
    this.gamesStatus = Array.from(document.querySelectorAll('.toggle-switch-checkbox'));
    this.updateGame = this.updateGame.bind(this);
    this.toggleStatus = this.toggleStatus.bind(this);
    this.addEventListeners();
  }
  async updateGame(evt) {
    evt.preventDefault();
    const g_name = evt.target.querySelector('.game-name').dataset.gameName;
    const g_path = evt.target.g_path.value;
    const g_executable = evt.target.g_executable.value;
    fetch(`/queue/${g_name}`, {
      method: 'put',
      headers: {
        'Content-Type': 'application/json',
        'authorization': `Bearer ${await idbKeyval.get('token')}`
      },
      body: JSON.stringify({
        g_name,
        g_path,
        g_executable
      })
    }).then(response => response.json()).then(response => Toast.Push(response.success)).catch(error => console.error(error));
  }
  async toggleStatus(evt) {
    const target = evt.target;
    fetch(`/queue/${g_name}`, {
      method: 'put',
      headers: {
        'Content-Type': 'application/json',
        'authorization': `Bearer ${await idbKeyval.get('token')}`
      },
      body: JSON.stringify({
        g_name: target.name,
        g_status: target.checked
      })
    }).then(response => response.json()).then(response => Toast.Push(response.success)).catch(error => console.error(error));
  }
  addEventListeners() {
    this.gamesUpdate.forEach(gameUpdate => gameUpdate.addEventListener('submit', this.updateGame));
    this.gamesStatus.forEach(gameStatus => gameStatus.addEventListener('click', this.toggleStatus));
  }
}

class App {
  constructor() {
    this.router();
  }
  router() {
    if (location.pathname === '/admin/login') {
      new Login();
    } else if (location.pathname === '/admin') {
      new Admin();
    }
  }
}
window.addEventListener('load', _ => new App());
