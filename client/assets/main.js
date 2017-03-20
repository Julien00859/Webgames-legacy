class WebGames {

    constructor() {
        /* Go to form */
        this._signInButton = document.querySelector('.signin-button');
        this._signUpButton = document.querySelector('.signup-button');

        /* Containers of forms */
        this._signInFormContainer = document.querySelector('.signin-form-container');
        this._signUpFormContainer = document.querySelector('.signup-form-container');

        this._signUp = document.querySelector('.signup-form');
        this._signIn = document.querySelector('.signin-form');
        this._cancelSignUp = document.querySelector('.cancel-form-signup-button');
        this._cancelSignIn = document.querySelector('.cancel-form-signin-button');

        this._showSignInForm = this._showSignInForm.bind(this);
        this._showSignUpForm = this._showSignUpForm.bind(this);
        this._login = this._login.bind(this);
        this._register = this._register.bind(this);
        this._cancelLogin = this._cancelLogin.bind(this);
        this._cancelRegister = this._cancelRegister.bind(this);

        this._addEventListeners();
    }

    _showSignInForm (evt) {
        evt.preventDefault();
        this._signInFormContainer.classList.add('signin-form-container__visible');
    }

    _showSignUpForm (evt) {
        evt.preventDefault();
        this._signUpFormContainer.classList.add('signup-form-container__visible');
    }

    _cancelLogin(evt) {
        evt.preventDefault();
        this._signInFormContainer.classList.remove('signin-form-container__visible');
    }

    _cancelRegister(evt) {
        evt.preventDefault();
        this._signUpFormContainer.classList.remove('signup-form-container__visible');
    }

    _login(evt) {
        evt.preventDefault();
        const form = evt.target;

        fetch('signin', {
            method: 'post',
            headers: {
                'Content-type': 'application/json'
            },
            body: JSON.stringify({
                login: form.pseudo.value,
                password: form.password.value
            })
        })
        .then(response => response.json())
        .then(credentials => {
            const { token, name} = credentials;
            console.log(name, token);
        })
        .then(_ => {
            requestAnimationFrame(_ => {
                this._signInFormContainer.classList.remove('signin-form-container__visible');
            })
        })
        .catch(err => console.warn(err));

    }

    _register(evt) {
        evt.preventDefault();
        const form = evt.target;

        fetch('signup', {
            method: 'post',
            headers: {
                'Content-type': 'application/json'
            },
            body: JSON.stringify({
                name: form.pseudo.value,
                email: form.email.value,
                password: form.password.value
            })
        })
        .then(response => response.text())
        .then(challenge => console.log(challenge))
        .then(_ => {
            requestAnimationFrame(_ => {
                this._signUpFormContainer.classList.remove('signup-form-container__visible');
            })
        })
        .catch(err => console.warn(err));

    }

    _addEventListeners() {
        this._signInButton.addEventListener('click', this._showSignInForm);
        this._signUpButton.addEventListener('click', this._showSignUpForm);

        this._cancelSignIn.addEventListener('click', this._cancelLogin);
        this._cancelSignUp.addEventListener('click', this._cancelRegister);

        this._signIn.addEventListener('submit', this._login);
        this._signUp.addEventListener('submit', this._register);
    }
}

window.addEventListener('load', _ => new WebGames());
