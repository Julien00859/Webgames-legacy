// Variable(s) Globale(s) //

let config = {
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

        class Player {
          constructor(name, x, y, image) {
            this.name = name;
            this.x = x;
            this.y = y;
            this.image = image;
          }
        }

        let players_collection = [];

        let game = new Phaser.Game(19 * 40, 15 * 40, Phaser.canvas, 'game', {preload: preload, create: create, update: update, render: render});

        let upKey, rightKey, leftKey, downKey, plantKey, fuseKey;

        function preload() {
            game.scale.scaleMode = Phaser.ScaleManager.SHOW_ALL;
            game.scale.pageAlignHorizontally = true;
            game.scale.pageAlignVertically = true;
            game.load.image("beam", "images/beam.png");
            game.load.image("rock", "images/rock.png");
            game.load.image("floor", "images/floor.png");
            game.load.image("p_1_S", "images/p_1_S.png");
            game.load.image("p_1_E", "images/p_1_E.png");
            game.load.image("p_1_N", "images/p_1_N.png");
            game.load.image("p_1_W", "images/p_1_W.png");
            game.load.image("p_2_S", "images/p_2_S.png");
            game.load.image("p_2_W", "images/p_2_W.png");
            game.load.image("p_2_E", "images/p_2_E.png");
            game.load.image("p_2_N", "images/p_2_N.png");
            game.load.image("bomb", "images/bomb.png", 40, 40);
            game.load.image("exp_x", "images/exp_x.png", 40, 40);
            game.load.image("exp_y", "images/exp_y.png", 40, 40);
            game.load.image("exp_c", "images/exp_c.png", 40, 40);
            game.load.image("B", "images/B.png", 40, 40);
            game.load.image("M", "images/M.png", 40, 40);
            game.load.image("P", "images/P.png", 40, 40);
            game.load.image("S", "images/S.png", 40, 40);
            game.load.image("H", "images/H.png", 40, 40);
        }

        function create() {

            upKey = game.input.keyboard.addKey(Phaser.Keyboard[config.upKey]);
            downKey = game.input.keyboard.addKey(Phaser.Keyboard[config.downKey]);
            leftKey = game.input.keyboard.addKey(Phaser.Keyboard[config.leftKey]);
            rightKey = game.input.keyboard.addKey(Phaser.Keyboard[config.rigthKey]);
            plantKey = game.input.keyboard.addKey(Phaser.Keyboard[config.plantKey]);
            fuseKey = game.input.keyboard.addKey(Phaser.Keyboard[config.fuseKey]);
            game.physics.startSystem(Phaser.Physics.ARCADE);

        }

        function update() {

            let players = io.players;

            if      (upKey.isDown)     io.send_event("move", {"direction": "N"});
            else if (downKey.isDown)   io.send_event("move", {"direction": "S"});
            else if (leftKey.isDown)   io.send_event("move", {"direction": "W"});
            else if (rightKey.isDown)  io.send_event("move", {"direction": "E"});
            else if (plantKey.isDown)  io.send_event("plant");
            else if (fuseKey.isDown)   io.send_event("fuse");

            game.input.keyboard.onUpCallback = function (e) {
                if (Phaser.Keyboard[config.upKey] || Phaser.Keyboard[config.downKey] || Phaser.Keyboard[config.leftKey] || Phaser.Keyboard[config.rigthKey]) io.send_event("stop");
            };

            for (let player in Object.keys(players)) {
              players_collection[player] = new Player("player " + Object.keys(players), players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20, "p_" + (parseInt(player) + 1) + "_" + players[Object.keys(players)[player]].direction)
            }

        }

        function render() {

            let map = io.map;
            let bombs = io.bombs;
            let explosions = io.explosions;
            let powerups = io.powerups;

            for (var x in map) { // Rendu de la map à partir de l'Array 2D
                for (var y in map[x]) {
                    //console.log(ligne, colonne);
                    if (map[x][y] == "#") game.add.sprite(x * 40, y * 40, "rock");
                    else if (map[x][y] == "&") game.add.sprite(x * 40, y * 40, "beam");
                    else if (map[x][y] == " ") game.add.sprite(x * 40, y * 40, "floor");
                }
            }

            for (let player of players_collection) {
              game.add.sprite(player.x, player.y, player.image);
            }

            for (let bomb in bombs) {
                game.add.sprite(bombs[bomb].position[0] * 40 - 20, bombs[bomb].position[1] * 40 - 20, "bomb");
            }

            for (let explosion in explosions) {
                //  X
                for (var i = explosions[explosion].position[0] - explosions[explosion].radius; i <= explosions[explosion].position[0] + explosions[explosion].radius; i++) {
                    //console.log(i);
                    //if (i <= 0) return;
                    game.add.sprite(i * 40 - 20, explosions[explosion].position[1] * 40 - 20, "exp_x");
                }

                // Y
                for (let i = explosions[explosion].position[1] - explosions[explosion].radius; i <= explosions[explosion].position[1] + explosions[explosion].radius; i++) {
                    //if (i <= 0) return;
                    game.add.sprite(explosions[explosion].position[0] * 40 - 20, i * 40 - 20, "exp_y");
                }

                game.add.sprite(explosions[explosion].position[0] * 40 - 20, explosions[explosion].position[1] * 40 - 20, "exp_c"); // Center
                exp_x.kill();
                exp_y.kill();
                exp_c.kill();

                for (let powerup in powerups) {
                    game.add.sprite(powerups[powerup][0] * 40 - 20, powerups[powerup][1] * 40 - 20, powerup);
                }
            }

        }

        // ------------------------------------------------------------------------------------------------------------------ //

        // Nouveau IO => Gère la communication client - serveur //

        io = new IO("localhost", 28456, this.game_name.value, game);

        // -------------------------------------------------------- //

    }); // Fin de la fonction onsubmit

} // Fin du main()
