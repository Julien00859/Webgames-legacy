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

        let game = new Phaser.Game(19 * 16, 15 * 16, Phaser.canvas, 'game', {preload: preload, create: create, update: update, render: render});

        let upKey, rightKey, leftKey, downKey, plantKey, fuseKey;

        let explo;

        function preload() {
            game.scale.scaleMode = Phaser.ScaleManager.SHOW_ALL;
            game.scale.pageAlignHorizontally = true;
            game.scale.pageAlignVertically = true;
            /*game.load.image("beam", "images/beam.png");
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
            game.load.image("bomb", "images/bomb.png");
            game.load.image("exp_x", "images/exp_x.png");
            game.load.image("exp_y", "images/exp_y.png");
            game.load.image("exp_c", "images/exp_c.png");
            game.load.image("B", "images/B.png");
            game.load.image("M", "images/M.png");
            game.load.image("P", "images/P.png");
            game.load.image("S", "images/S.png");
            game.load.image("H", "images/H.png");
            game.load.spritesheet('exp', 'images/eKD88.png', 32, 32);*/

            game.load.spritesheet('grass', 'images/grass.png', 16, 16);
            game.load.spritesheet('wall', 'images/wall.png', 16, 16);
            game.load.spritesheet('player', 'images/player_spritesheet.png', 16, 16);
            game.load.spritesheet('player2', 'images/enemy_spritesheet.png', 16, 16);
            game.load.spritesheet('bomb', 'images/bomb_spritesheet.png', 16, 16);
            game.load.image('exp', 'images/explosion.png');

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

            let map = io.map;
            let players = io.players;
            let bombs = io.bombs;
            let explosions = io.explosions;
            let powerups = io.powerups;
            let rendered = false;
            let mapChanging = [];
            const delay = 3000;

              for (let x in map) { // Rendu de la map à partir de l'Array 2D
                  for (let y in map[x]) {
                      //console.log(ligne, colonne);
                      if (map[x][y] == "#") {
                        let sprite = game.add.sprite(x * 16, y * 16, "wall", 1);
                      }
                      else if (map[x][y] == "&") {
                        let sprite = game.add.sprite(x * 16, y * 16, "wall", 3);
                      }
                      else if (map[x][y] == " ") {
                        let sprite = game.add.image(x * 16, y * 16, "grass", 1);
                      }
                  }
              }
              rendered = true;


            for (let player in Object.keys(players)) {
              let play = game.add.sprite(players[Object.keys(players)[player]].position[0] * 16 - 8,
                                          players[Object.keys(players)[player]].position[1] * 16 - 8,
                                          'player' /*${(parseInt(player) + 1)}*/,
                                          1
                                        );

              switch(players[Object.keys(players)[player]].direction) {
                case "S": play.animations.add("walking_down", [1, 2, 3], 10, true);
                  play.animations.play('walking_down');
                  break;
                case "W": play.animations.add("walking_left", [4, 5, 6, 7], 10, true);
                  play.animations.play('walking_left');
                  break;
                case "E": play.animations.add("walking_right", [4, 5, 6, 7], 10, true);
                  play.animations.play('walking_right');
                  break;
                case "N": play.animations.add("walking_up", [0, 8, 9], 10, true);
                  play.animations.play('walking_up');
                  break;
              }
            }

            if (bombs != {}) {
              for (let bomb in bombs) {
                  let bomb_animation = game.add.sprite(bombs[bomb].position[0] * 16 - 8, bombs[bomb].position[1] * 16 - 8, "bomb");
                  bomb_animation.animations.add('bomb', [0, 1, 2, 3, 4, 5], 10, true);
                  bomb_animation.animations.play('bomb', 10, true);
                  setTimeout(function() {
                    delete bombs[bomb] // Supprime la bombe
                  }, delay)

              }
            }

            if (explosions != {}) {
              for (let explosion in explosions) {
                  //  X
                  for (let i = explosions[explosion].position[0] - explosions[explosion].radius; i <= explosions[explosion].position[0] + explosions[explosion].radius; i++) {
                      if (i > 0 || i < 18) {
                        console.log(i);
                        let explo = game.add.image(i * 16 - 8, explosions[explosion].position[1] * 16 - 8, "exp");
                        let index_x = Math.floor(i)
                        let index_y = Math.floor(explosions[explosion].position[1])
                        io.map[index_y][index_x] = [i, explosions[explosion].position[1]]
                        //mapChanging.push([i * 16 - 8, explosions[explosion].position[1] * 16 - 8])
                        //let sprite = game.add.sprite(i * 16, explosions[explosion].position[1] * 16, "grass", 1);
                        //explo.animations.add('boom', [2, 9, 16, 23]);
                        //explo.animations.play('boom', 30, false, true);

                      }

                  }

                  // Y
                  for (let i = explosions[explosion].position[1] - explosions[explosion].radius; i <= explosions[explosion].position[1] + explosions[explosion].radius; i++) {
                    if (i > 0) {
                      let explo = game.add.image(explosions[explosion].position[0] * 16 - 8, i * 16 - 8, "exp");
                      let index_x = Math.floor(explosions[explosion].position[0])
                      let index_y = Math.floor(i)
                      io.map[index_y][index_x] = [explosions[explosion].position[0], i]
                      //mapChanging.push([explosions[explosion].position[0] * 16 - 8, i * 16 - 8])
                      //let sprite = game.add.sprite(explosions[explosion].position[0] * 16, i * 16, "grass", 1);
                      //let boom = exp.animations.add('boom', [3, 10, 17, 24]);
                      //exp.animations.play('boom', 30, false, true);
                    }

                    /*let exp_c = game.add.sprite(explosions[explosion].position[0] * 16 - 8, i * 16 - 8, "exp");
                    let boom = exp_c.animations.add('boom', [0, 7, 14, 21]);
                    exp_c.animations.play('boom', 30, false, true);*/

                  }


                  /*for (let powerup in powerups) {
                      console.log(powerups);
                      game.add.sprite(powerup[0] * 16 - 8, powerup[1] * 16 - 8, powerups[powerup]);
                  }*/

                  setTimeout(function() {
                    delete explosions[explosion] // Supprime l'explosion
                  }, delay)
              }
            }

            /*mapChanging.forEach(position => {
              game.add.sprite(position[0], position[1], "grass", 1)
            });*/

        }

        // ------------------------------------------------------------------------------------------------------------------ //

        // Nouveau IO => Gère la communication client - serveur //

        io = new IO("localhost", 28456, this.game_name.value, game);

        // -------------------------------------------------------- //

    }); // Fin de la fonction onsubmit

} // Fin du main()
