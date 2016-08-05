// Variable(s) Globale(s) //

var config = {
    upKey: "Z",
    downKey: "S",
    leftKey: "Q",
    rigthKey: "D",
    plantKey: "O",
    fuseKey: "P"
}

// --------------------- //

function main() {

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

    // ----a---------------------------------------------------------------------- //

    document.getElementById("select_game").addEventListener("submit", function(event){
        event.preventDefault();

        var game = new Phaser.Game(800, 600, Phaser.auto, 'game', {preload: preload, create: create, update: update, render: render});

        var upKey, rightKey, leftKey, downKey, plantKey, fuseKey;

        function preload() {
            game.load.image("beam", "images/beam.png");
            game.load.image("rock", "images/rock.png");
            game.load.image("floor", "images/floor.png");
            game.load.image("p_1_down", "images/p_1_down.png");
            game.load.image("p_1_right", "images/p_1_right.png");
            game.load.image("p_1_up", "images/p_1_up.png");
            game.load.image("p_1_left", "images/p_1_left.png");
            game.load.image("p_2_down", "images/p_2_down.png");
            game.load.image("p_2_left", "images/p_2_left.png");
            game.load.image("p_2_right", "images/p_2_right.png");
            game.load.image("p_2_up", "images/p_2_up.png");
            game.load.image("bomb", "images/bomb.png");
            game.load.image("exp_x", "images/exp_x.png");
            game.load.image("exp_y", "images/exp_y.png");
            game.load.image("exp_c", "images/exp_c.png");
            game.load.image("B", "images/B.png");
            game.load.image("M", "images/M.png");
            game.load.image("P", "images/P.png");
            game.load.image("S", "images/S.png");
            game.load.image("H", "images/H.png");

        }

        function create() {

            upKey = game.input.keyboard.addKey(Phaser.Keyboard[config.upKey]);
            downKey = game.input.keyboard.addKey(Phaser.Keyboard[config.downKey]);
            leftKey = game.input.keyboard.addKey(Phaser.Keyboard[config.leftKey]);
            rightKey = game.input.keyboard.addKey(Phaser.Keyboard[config.rigthKey]);
            plantKey = game.input.keyboard.addKey(Phaser.Keyboard[config.plantKey]);
            fuseKey = game.input.keyboard.addKey(Phaser.Keyboard[config.fuseKey]);

        }

        function update() {

            if      (upKey.isDown)     io.send_event("move", {"direction": "N"});
            else if (downKey.isDown)   io.send_event("move", {"direction": "S"});
            else if (leftKey.isDown)   io.send_event("move", {"direction": "W"});
            else if (rightKey.isDown)  io.send_event("move", {"direction": "E"});
            else if (plantKey.isDown)  io.send_event("plant");
            else if (fuseKey.isDown)   io.send_event("fuse");

            game.input.keyboard.onUpCallback = function (e) {
                if (Phaser.Keyboard[config.upKey] || Phaser.Keyboard[config.downKey] || Phaser.Keyboard[config.leftKey] || Phaser.Keyboard[config.rigthKey]) io.send_event("stop");
            };

        }

        function render() {

            var map = io.map;
            var players = io.players;
            var bombs = io.bombs;
            var explosions = io.explosions;
            var powerups = io.powerups;

            for (var x in io.map) { // Rendu de la map à partir de l'Array 2D
                for (var y in io.map[x]) {
                    //console.log(ligne, colonne);
                    if (io.map[x][y] == "#") game.add.sprite(x * 40, y * 40, "rock");
                    else if (io.map[x][y] == "&") game.add.sprite(x * 40, y * 40, "beam");
                    else if (io.map[x][y] == " ") game.add.sprite(x * 40, y * 40, "floor");
                }
            }

            for (var player in Object.keys(players)) {
                switch (players[Object.keys(players)[player]].direction) {
                    case "N": game.add.sprite(players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20, "p_" + (parseInt(player) + 1) + "_up" )
                        break;
                    case "S": game.add.sprite(players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20, "p_" + (parseInt(player) + 1) + "_down")
                        break;
                    case "E": game.add.sprite(players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20, "p_" + (parseInt(player) + 1) + "_right")
                        break;
                    case "W": game.add.sprite(players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20, "p_" + (parseInt(player) + 1) + "_left")
                        break;
                }
            }

            for (var bomb in bombs) {
                game.add.sprite(bombs[bomb].position[0] * 40 - 20, bombs[bomb].position[1] * 40 - 20, "bomb", 40, 40);
            }

            for (var explosion in explosions) {
                //  X
                for (var i = explosions[explosion].position[0] - explosions[explosion].radius; i <= explosions[explosion].position[0] + explosions[explosion].radius; i++) {
                    //console.log(i);
                    //if (i <= 0) return;
                    game.add.sprite(i * 40 - 20, explosions[explosion].position[1] * 40 - 20, "exp_x", 40, 40);
                }

                // Y
                for (var i = explosions[explosion].position[1] - explosions[explosion].radius; i <= explosions[explosion].position[1] + explosions[explosion].radius; i++) {
                    //if (i <= 0) return;
                    game.add.sprite(explosions[explosion].position[0] * 40 - 20, i * 40 - 20, "exp_y", 40, 40);
                }

                game.add.sprite(explosions[explosion].position[0] * 40 - 20, explosions[explosion].position[1] * 40 - 20, "exp_c", 40, 40); // Center

                for (var powerup in powerups) {
                    this.layer.drawImage(this.image[powerup], powerups[powerup][0] * 40 - 20, powerups[powerup][1] * 40 - 20, 40, 40);
                }
            }

        }

        // ------------------------------------------------------------------------------------------------------------------ //

        // Nouveau IO => Gère la communication client - serveur //

        io = new IO("localhost", 28456, this.game_name.value, game);

        // -------------------------------------------------------- //

    }); // Fin de la fonction onsubmit

} // Fin du main()
