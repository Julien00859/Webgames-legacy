let loadState = {

	preload: function() {

		// Loading text
		let loadingLabel = game.add.text(40, 150, 'chargement...',  {font: '20px Arial', fill: '#fff'})

		// Loading of the assets

        game.load.spritesheet('map', 'images/sprite/map_2.png', 16, 16);
        game.load.spritesheet('player', 'images/sprite/player1.png', 18, 21);
        //game.load.spritesheet('player2', 'images/player2.png', 17, 20);
        game.load.spritesheet('bomb', 'images/sprite/bomb.png', 16, 16);
        //game.load.spritesheet('exp', 'images/sprite/explo.png', 76.5, 80);
		game.load.spritesheet('exp_c', 'images/sprite/exp_c.png', 16, 16);
		game.load.spritesheet('exp_x', 'images/sprite/exp_x.png', 16, 16);
		game.load.spritesheet('exp_y', 'images/sprite/exp_y.png', 16, 16);
		game.load.spritesheet('exp_x_droite', 'images/sprite/exp_x_droite.png', 16, 16);
		game.load.spritesheet('exp_x_gauche', 'images/sprite/exp_x_gauche.png', 16, 16);
		game.load.spritesheet('exp_y_bas', 'images/sprite/exp_y_bas.png', 16, 16);
		game.load.spritesheet('exp_y_haut', 'images/sprite/exp_y_haut.png', 16, 16);

	},

	create: function() {
		game.state.start('menu')
	}
}
