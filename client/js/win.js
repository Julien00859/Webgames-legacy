let winState = {

	create: function() {
		
		let winLabel = game.add.text(40, 80, `Le joueur ${io.winner} a gagné !!`, {font: '25px Arial', fill: "#fff"})

		let startLabel = game.add.text(40, game.world.height - 80, "Appuyer sur la barre d'espace pour revenir au menu", {font: '15px Arial', fill: "#fff"})

		let spaceKey = game.input.keyboard.addKey(Phaser.keyboard.SPACEBAR)

		spaceKey.onDown.addOnce(this.restart, this);
	},

	restart: function () {
		game.state.start('menu')
	}
}