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
      body: JSON.stringify({
        username,
        password
      })
    }).then(response => response.json())
      .then(response => {
        if (response.error) {
          Toast.Push(response.error.join('')); /// to change :)
          return;
        }
        saveToken(response.token)
      })
      .catch(error => console.error(error));
  }

  saveToken(token) {
    console.log(token);
    localStorage.setItem('token', token);
  }

  addEventListeners() {
    this.form.addEventListener('submit', this.loginAdmin);
  }
}

class Toast {
  static Push(message, options = {duration: 3000}) {
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

window.addEventListener('load', _ => new Login());
