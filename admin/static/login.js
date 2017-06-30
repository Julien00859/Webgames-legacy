class Login {
  constructor() {

  }

  loginAdmin(evt) {
    evt.preventDefault();
  }
}

window.addEventListener('load', _ => new Login());
