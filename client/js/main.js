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

    // --------------------------------------------------------------------------- //

    document.getElementById("select_game").addEventListener("submit", function(event){
        event.preventDefault();

        let game = new Phaser.Game(19 * 16, 15 * 16, Phaser.canvas, 'game', {preload: preload, create: create, update: update, render: render});

        let upKey, rightKey, leftKey, downKey, plantKey, fuseKey;

        let play, explo, exp_c, bomb_animation;

        function preload() {
            game.scale.scaleMode = Phaser.ScaleManager.SHOW_ALL;
            game.scale.pageAlignHorizontally = true;
            game.scale.pageAlignVertically = true;

            game.load.spritesheet('map', 'images/sprite/map_2.png', 16, 16);
            game.load.spritesheet('player', 'images/sprite/player1.png', 18, 21);
            //game.load.spritesheet('player2', 'images/player2.png', 17, 20);
            game.load.spritesheet('bomb', 'images/sprite/bomb.png', 16, 16);
            game.load.spritesheet('exp', 'images/sprite/explo.png', 76.5, 80);

        }

        function create() {

            upKey = game.input.keyboard.addKey(Phaser.Keyboard[config.upKey]);
            downKey = game.input.keyboard.addKey(Phaser.Keyboard[config.downKey]);
            leftKey = game.input.keyboard.addKey(Phaser.Keyboard[config.leftKey]);
            rightKey = game.input.keyboard.addKey(Phaser.Keyboard[config.rigthKey]);
            plantKey = game.input.keyboard.addKey(Phaser.Keyboard[config.plantKey]);
            fuseKey = game.input.keyboard.addKey(Phaser.Keyboard[config.fuseKey]);

            game.physics.startSystem(Phaser.Physics.ARCADE);

            exp_c = game.add.sprite(150, 150, "exp");
            exp_c.animations.add('boom');
            exp_c.animations.play('boom', 30, false, true);

            bomb_animation = game.add.sprite(48, 32, "bomb");
            bomb_animation.animations.add('bomb');
            bomb_animation.animations.play('bomb', 10, true);



        }

        function update() {

          let players = io.players;
          let bombs = io.bombs;
          let explosions = io.explosions;
          let powerups = io.powerups;
          const delay = 3000;

          if      (upKey.isDown)     io.send_event("move", {"direction": "N"});
          else if (downKey.isDown)   io.send_event("move", {"direction": "S"});
          else if (leftKey.isDown)   io.send_event("move", {"direction": "W"});
          else if (rightKey.isDown)  io.send_event("move", {"direction": "E"});
          else if (plantKey.isDown)  io.send_event("plant");
          else if (fuseKey.isDown)   io.send_event("fuse");

          //if (upKey.isUp || downKey.isUp || leftKey.isUp || rigthKey.isUp) io.send_event("stop")

          game.input.keyboard.onUpCallback = function (e) {
              if (Phaser.Keyboard[config.upKey] || Phaser.Keyboard[config.downKey] || Phaser.Keyboard[config.leftKey] || Phaser.Keyboard[config.rigthKey]) io.send_event("stop");
          };

          for (let player in Object.keys(players)) {
            game.add.sprite(players[Object.keys(players)[player]].position[0] * 16 - 8,
                                      players[Object.keys(players)[player]].position[1] * 16 - 8,
                                      'player' /*${(parseInt(player) + 1)}*/,
                                      1
                                    );
            /*switch(players[Object.keys(players)[player]].direction) {
              case "S": play.animations.add("walking_down", [6, 7, 8], 10, true);
                play.animations.play('walking_down');
                break;
              case "W": play.animations.add("walking_left", [0, 1, 2], 10, true);
                play.animations.play('walking_left');
                break;
              case "E": play.animations.add("walking_right", [0, 1, 2], 10, true);
                play.animations.play('walking_right');
                break;
              case "N": play.animations.add("walking_up", [3, 4, 5], 10, true);
                play.animations.play('walking_up');
                break;
            }*/
          }


          if (bombs != {}) {
            for (let bomb in bombs) {
                bomb_animation.x = bombs[bomb].position[0] * 16 - 8
                bomb_animation.y = bombs[bomb].position[1] * 16 - 8
                setTimeout(function() {
                  delete bombs[bomb] // Supprime la bombe
                }, delay)

            }
          }

          if (explosions != {}) {
            for (let explosion in explosions) {

              exp_c.x =  explosions[explosion].position[0] * 76.5 - 38.25
              exp_c.y =  explosions[explosion].position[1] * 80 - 40

                //  X
                for (let i = explosions[explosion].position[0] - explosions[explosion].radius; i <= explosions[explosion].position[0] + explosions[explosion].radius; i++) {
                    if (i > 1 || i < 18) {
                      //let explo = game.add.image(i * 16 - 8, explosions[explosion].position[1] * 16 - 8, "exp");
                      let index_x = Math.floor(i)
                      let index_y = Math.floor(explosions[explosion].position[1])
                      io.map[index_y][index_x] = " "

                    }

                }

                // Y
                for (let i = explosions[explosion].position[1] - explosions[explosion].radius; i <= explosions[explosion].position[1] + explosions[explosion].radius; i++) {
                  if (i > 1 || i < 14) {
                    let index_x = Math.floor(explosions[explosion].position[0])
                    let index_y = Math.floor(i)
                    io.map[index_y][index_x] = "#"
                  }
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


        }

        function render() {

            let map = io.map;

            for (let x in map) { // Rendu de la map à partir de l'Array 2D
                for (let y in map[x]) {
                    //console.log(ligne, colonne);
                    if (map[x][y] == "#") {
                      let sprite = game.add.sprite(x * 16, y * 16, "map", 1);
                    }
                    else if (map[x][y] == "&") {
                      let sprite = game.add.sprite(x * 16, y * 16, "map", 2);
                    }
                    else if (map[x][y] == " ") {
                      let sprite = game.add.image(x * 16, y * 16, "map", 0);
                    }
                }
            }





        }

        // ------------------------------------------------------------------------------------------------------------------ //

        // Nouveau IO => Gère la communication client - serveur //

        io = new IO("localhost", 28456, this.game_name.value, game);

        // -------------------------------------------------------- //

    }); // Fin de la fonction onsubmit

} // Fin du main()
