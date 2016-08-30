let plays = [];

class Player {
	constructor(id, x, y, pos){
		this.sprite = null
		this.id = id
		this.x = x
		this.y = y
		this.pos = pos

		this.last = {x: x, y: y}

		this.create = this.create.bind(this)
		this.update = this.update.bind(this)

		this.create()
	}

	create() {
		console.log('creating user...')
		this.sprite = game.add.sprite(this.x, this.y, 'player', 1)

		this.sprite.frame = 6;

		//this.sprite.animations.add("walking_down", [6, 7, 8], 10, true);
		//this.sprite.animations.add("walking_left", [0, 1, 2], 10, true);
		//this.sprite.animations.add("walking_right", [0, 1, 2], 10, true);
		//this.sprite.animations.add("walking_up", [3, 4, 5], 10, true);

		game.physics.enable(this.sprite, Phaser.Physics.ARCADE);
	}

	update() {
		if (!this.sprite)
			return

		if (this.x !== this.last.x || this.y !== this.last.y) {

			this.sprite.x = this.x
			this.sprite.y = this.y

			/*switch(this.pos) {
				case "S":
					this.sprite.animations.play('walking_down');
					break;
				case "W":
					this.sprite.animations.play('walking_left');
					break;
				case "E":
					this.sprite.animations.play('walking_right');
					break;
				case "N":
					this.sprite.animations.play('walking_up');
					break;
			}*/

			this.last.x = this.x
			this.last.y = this.y

		}

	}
}

let playState = {

	create: function() {

	    upKey = game.input.keyboard.addKey(Phaser.Keyboard[config.upKey]);
	    downKey = game.input.keyboard.addKey(Phaser.Keyboard[config.downKey]);
	    leftKey = game.input.keyboard.addKey(Phaser.Keyboard[config.leftKey]);
	    rightKey = game.input.keyboard.addKey(Phaser.Keyboard[config.rigthKey]);
	    plantKey = game.input.keyboard.addKey(Phaser.Keyboard[config.plantKey]);
	    fuseKey = game.input.keyboard.addKey(Phaser.Keyboard[config.fuseKey]);

	    let map = io.map;
		let players = io.players;

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

		for (let player in players) {
			plays.push(new Player(player, players[player].position[0] * 16 - 8, players[player].position[1] * 16 - 8, players[player].direction))
		}
	},

	update: function() {

      let players = io.players;
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

		for (let player in players) {

			for (let el of plays) {
				if (player == el.id) {
					el.x = players[player].position[0] * 16 - 8
					el.y = players[player].position[1] * 16 - 8
					el.pos = players[player].direction
					el.update()
				}
			}

		}

    }
}

function handleBomb() {

  let bombs = io.bombs

  if (bombs != {}) {
    for (let bomb in bombs) {
        //bomb_animation.x = bombs[bomb].position[0] * 16 - 8
        //bomb_animation.y = bombs[bomb].position[1] * 16 - 8

        bomb_animation = game.add.sprite(bombs[bomb].position[0] * 16 - 8, bombs[bomb].position[1] * 16 - 8, "bomb");
        bomb_animation.animations.add('bomb');
        bomb_animation.animations.play('bomb', 10);
    }
  }

}

function handleExplosion() {

    let explosions = io.explosions

    if (explosions != {}) {
      for (let explosion in explosions) {
          console.log("explosion...")

		  /* EXPLOSION -- ANIMATION */
		  // C
		  exp_c = game.add.sprite(explosions[explosion].position[0] * 16 - 8, explosions[explosion].position[1] * 16 - 8, "exp_c");
		  exp_c.animations.add('boom');
		  exp_c.animations.play('boom', 5, false, true);
		  // X
		  for (let i = explosions[explosion].position[0] - explosions[explosion].radius; i <= explosions[explosion].position[0] + explosions[explosion].radius; i++) {

			  if (i >= 1 && i <= 18) {
				  let index_x = Math.floor(i)
				  let index_y = Math.floor(explosions[explosion].position[1])

	            exp_x = game.add.sprite(index_x * 16, index_y * 16, "exp_x");
	            exp_x.animations.add('boom');
	            exp_x.animations.play('boom', 5, false, true);
			  }
		  }

		  // Y
		  for (let i = explosions[explosion].position[1] - explosions[explosion].radius; i <= explosions[explosion].position[1] + explosions[explosion].radius; i++) {

			  if (i >= 1 && i <= 14) {
				  let index_x = Math.floor(explosions[explosion].position[0])
				  let index_y = Math.floor(i)

  	            exp_y = game.add.sprite(index_x * 16, index_y * 16, "exp_y");
  	            exp_y.animations.add('boom');
  	            exp_y.animations.play('boom', 5, false, true);

			  }
		  }

          /*exp_c = game.add.sprite(explosions[explosion].position[0] * 76.5 - 38.25, explosions[explosion].position[1] * 80 - 40, "exp");
          exp_c.animations.add('boom');
          exp_c.animations.play('boom', 5, false, true);*/

		  /* EXPLOSION -- MODIF DE LA MAP */
          setTimeout(function() {
            //  X
            for (let i = explosions[explosion].position[0] - explosions[explosion].radius; i <= explosions[explosion].position[0] + explosions[explosion].radius; i++) {

                if (i >= 1 && i <= 18) {
					console.log(i, i >= 1)
                  	let index_x = Math.floor(i)
                  	let index_y = Math.floor(explosions[explosion].position[1])
				  	//console.log(index_x, index_y)
					let sprite = game.add.image(index_x * 16, index_y * 16, "map", 0);
                }
            }

            // Y
            for (let i = explosions[explosion].position[1] - explosions[explosion].radius; i <= explosions[explosion].position[1] + explosions[explosion].radius; i++) {

	          	if (i >= 1 && i <= 14) {
		            let index_x = Math.floor(explosions[explosion].position[0])
		            let index_y = Math.floor(i)
					//console.log(index_x, index_y)
					let sprite = game.add.image(index_x * 16, index_y * 16, "map", 0);
	          	}
            }
          }, 1000);

      }
    }

}

function handlePowerups() {

  /*for (let powerup in powerups) {
      console.log(powerups);
      game.add.sprite(powerup[0] * 16 - 8, powerup[1] * 16 - 8, powerups[powerup]);
  }*/

}
