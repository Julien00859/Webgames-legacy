let config = {
    upKey: "Z",
    downKey: "S",
    leftKey: "Q",
    rigthKey: "D",
    plantKey: "O",
    fuseKey: "P"
}

let io;
let game;

// Config des touches //

document.getElementById("config").addEventListener("submit", function(event){
    event.preventDefault();
    config.upKey = this.upKey.value;
    config.downKey = this.downKey.value;
    config.leftKey = this.leftKey.value;
    config.rigthKey = this.rigthKey.value;
    config.plantKey = this.plantKey.value;
    config.fuseKey = this.fuseKey.value;
});

document.getElementById("select_game").addEventListener("submit", function(event){
	event.preventDefault(); // PreventDefault

	game = new Phaser.Game(19 * 16, 15 * 16, Phaser.AUTO, 'game') // Launch game

	io = new IO("localhost", 28456, this.game_name.value, game); // Connexion 

	// States
	game.state.add('boot', bootState) 
	game.state.add('load', loadState)
	game.state.add('menu', menuState)
	game.state.add('play', playState)
	game.state.add('win', winState)


	game.state.start('boot') // Launch Boot state

})