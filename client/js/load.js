let loadState = {

	preload: function() {
		
		// Loading text
		let loadingLabel = game.add.text(40, 150, 'chargement...',  {font: '20px Arial', fill: '#fff'})
		
		// Loading of the assets

        game.load.spritesheet('map', 'images/sprite/map_2.png', 16, 16);
        game.load.spritesheet('player', 'images/sprite/player1.png', 18, 21);
        //game.load.spritesheet('player2', 'images/player2.png', 17, 20);
        game.load.spritesheet('bomb', 'images/sprite/bomb.png', 16, 16);
        game.load.spritesheet('exp', 'images/sprite/explo.png', 76.5, 80);

	},

	create: function() {
		game.state.start('menu') 
	}
}