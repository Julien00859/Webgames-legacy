let menuState = {
	create: function() {

		let nameLabel = game.add.text(60, 80, "BOMBERMAN", {font: '25px Arial', fill: '#fff'})

		let startLabel = game.add.text(60, game.world.height - 80, "Appuyez sur la barre d'espace", {font: '15px Arial', fill: '#fff'})

		let spaceKey = game.input.keyboard.addKey(Phaser.Keyboard.SPACEBAR);

		spaceKey.onDown.addOnce(this.start, this)

	},

	start: function() {
		if (!io.ready) {
			game.add.text(60, game.world.height - 110, "En attente d'un second joueur...", {font: "15px Arial", fill: "#fff"})
			return
		}

		game.state.start('play')
	}
}