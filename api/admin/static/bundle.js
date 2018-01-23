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

var js_cookie = createCommonjsModule(function (module, exports) {
(function (factory) {
	var registeredInModuleLoader = false;
	if (typeof undefined === 'function' && undefined.amd) {
		undefined(factory);
		registeredInModuleLoader = true;
	}
	{
		module.exports = factory();
		registeredInModuleLoader = true;
	}
	if (!registeredInModuleLoader) {
		var OldCookies = window.Cookies;
		var api = window.Cookies = factory();
		api.noConflict = function () {
			window.Cookies = OldCookies;
			return api;
		};
	}
}(function () {
	function extend () {
		var i = 0;
		var result = {};
		for (; i < arguments.length; i++) {
			var attributes = arguments[ i ];
			for (var key in attributes) {
				result[key] = attributes[key];
			}
		}
		return result;
	}
	function init (converter) {
		function api (key, value, attributes) {
			var result;
			if (typeof document === 'undefined') {
				return;
			}
			if (arguments.length > 1) {
				attributes = extend({
					path: '/'
				}, api.defaults, attributes);
				if (typeof attributes.expires === 'number') {
					var expires = new Date();
					expires.setMilliseconds(expires.getMilliseconds() + attributes.expires * 864e+5);
					attributes.expires = expires;
				}
				attributes.expires = attributes.expires ? attributes.expires.toUTCString() : '';
				try {
					result = JSON.stringify(value);
					if (/^[\{\[]/.test(result)) {
						value = result;
					}
				} catch (e) {}
				if (!converter.write) {
					value = encodeURIComponent(String(value))
						.replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g, decodeURIComponent);
				} else {
					value = converter.write(value, key);
				}
				key = encodeURIComponent(String(key));
				key = key.replace(/%(23|24|26|2B|5E|60|7C)/g, decodeURIComponent);
				key = key.replace(/[\(\)]/g, escape);
				var stringifiedAttributes = '';
				for (var attributeName in attributes) {
					if (!attributes[attributeName]) {
						continue;
					}
					stringifiedAttributes += '; ' + attributeName;
					if (attributes[attributeName] === true) {
						continue;
					}
					stringifiedAttributes += '=' + attributes[attributeName];
				}
				return (document.cookie = key + '=' + value + stringifiedAttributes);
			}
			if (!key) {
				result = {};
			}
			var cookies = document.cookie ? document.cookie.split('; ') : [];
			var rdecode = /(%[0-9A-Z]{2})+/g;
			var i = 0;
			for (; i < cookies.length; i++) {
				var parts = cookies[i].split('=');
				var cookie = parts.slice(1).join('=');
				if (cookie.charAt(0) === '"') {
					cookie = cookie.slice(1, -1);
				}
				try {
					var name = parts[0].replace(rdecode, decodeURIComponent);
					cookie = converter.read ?
						converter.read(cookie, name) : converter(cookie, name) ||
						cookie.replace(rdecode, decodeURIComponent);
					if (this.json) {
						try {
							cookie = JSON.parse(cookie);
						} catch (e) {}
					}
					if (key === name) {
						result = cookie;
						break;
					}
					if (!key) {
						result[name] = cookie;
					}
				} catch (e) {}
			}
			return result;
		}
		api.set = api;
		api.get = function (key) {
			return api.call(api, key);
		};
		api.getJSON = function () {
			return api.apply({
				json: true
			}, [].slice.call(arguments));
		};
		api.defaults = {};
		api.remove = function (key, attributes) {
			api(key, '', extend(attributes, {
				expires: -1
			}));
		};
		api.withConverter = init;
		return api;
	}
	return init(function () {});
}));
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
      Toast.Push(response.success, { duration: 5000 });
      this.saveToken(response.token);
    }).catch(error => console.error(error));
  }
  async saveToken(token) {
    js_cookie.set('jwt', token, { expires: 1 });
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
