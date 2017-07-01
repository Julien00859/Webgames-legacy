class Admin {
  constructor() {
    this.gamesUpdate = Array.from(document.querySelectorAll('.game-form'));
    this.gamesStatus = Array.from(document.querySelectorAll('.game-toggle-status'));

    this.updateGame = this.updateGame.bind(this);
    this.toggleStatus = this.toggleStatus.bind(this);

    this.addEventListeners();
  }

  updateGame(evt) {
    evt.preventDefault();

    const {g_path, g_executable} = evt.target;

    fetch('/admin/update', {
      method: 'post',
      body: {
        g_path,
        g_executable
      }
    }).then(response => {
      console.log('jeu mis à jour');
    }).catch(error => console.error(error));
  }

  toggleStatus(evt) {
    console.log(evt)
    const target = evt.currentTarget;
    const isEnabled = target.dataset.enabled;

    target.classList.toggle('enabled');
    target.dataset.enabled = !isEnabled;

    fetch('/admin/update', {
      method: 'post',
      body: {
        g_status: !isEnabled
      }
    }).then(response => {
      console.log('status changé');
    }).catch(error => console.error(error));
  }

  addEventListeners() {
    //this.gamesUpdate.forEach(gameUpdate => gameUpdate.addEventListener('submit', this.updateGame));
    this.gamesStatus.forEach(gameStatus => gameStatus.addEventListener('click', this.toggleStatus));
  }
}

window.addEventListener('load', _ => new Admin());
