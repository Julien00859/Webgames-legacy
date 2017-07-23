import Toast from './toast.js';
import cookies from 'js-cookie';

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
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        username,
        password
      })
    }).then(response => response.json())
      .then(response => {
        if (response.error) {
          Toast.Push(response.error); /// to change :)
          return;
        }
        Toast.Push(response.success, {duration: 5000});
        this.saveToken(response.token);
      })
      .catch(error => console.error(error));
  }

  saveToken(token) {
    cookies.set('token', token, {expires: 1});
  }

  addEventListeners() {
    this.form.addEventListener('submit', this.loginAdmin);
  }
}

export default Login;
