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

    const g_path = evt.target.g_path;
    const g_executable = evt.target.g_executable;

    fetch('/admin/update', {
      method: 'put',
      headers: {
        'Content-Type': 'application/json',
        'authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        g_name,
        g_path,
        g_executable
      })
    }).then(response => response.json())
      .then(response => Toast.Push(response.success))
      .catch(error => console.error(error));
  }

  toggleStatus(evt) {
    const target = evt.currentTarget.querySelector('.toggle-switch-checkbox');

    fetch('/admin/update', {
      method: 'put',
      headers: {
        'Content-Type': 'application/json',
        'authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        g_name : target.name,
        g_status: target.checked
      })
    }).then(response => response.json())
      .then(response => Toast.Push(response.success))
      .catch(error => console.error(error));
  }

  addEventListeners() {
    this.gamesUpdate.forEach(gameUpdate => gameUpdate.addEventListener('submit', this.updateGame));
    //this.gamesStatus.forEach(gameStatus => gameStatus.addEventListener('click', this.toggleStatus));
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

window.addEventListener('load', _ => new Admin());
