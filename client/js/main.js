config = {
    upKey: "z",
    downKey: "s",
    leftKey: "q",
    rigthKey: "d",
    plantKey: "o",
    fuseKey: "p"
}

// Variable(s) Globale(s) //

var map = {}


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

    // -------------------------------------------------------------------------- //

    document.getElementById("select_game").addEventListener("submit", function(event){
        event.preventDefault();

        // Playground => S'occupe du rendu graphique, sonore du jeu //

        var app = playground({
            // BOMBERMAN
            container: document.querySelector("#game"),

            keydown: function(event) {

                if      (event.key == config.upKey)     io.send_event("move", {"direction": "N"});
                else if (event.key == config.downKey)   io.send_event("move", {"direction": "S"});
                else if (event.key == config.leftKey)   io.send_event("move", {"direction": "W"});
                else if (event.key == config.rigthKey)  io.send_event("move", {"direction": "E"});
                else if (event.key == config.plantKey)  io.send_event("plant");
                else if (event.key == config.fuseKey)   io.send_event("fuse");

            },

            keyup: function(event) {

                if (
                    event.key == config.upKey ||
                    event.key == config.downKey ||
                    event.key == config.leftKey ||
                    event.key == config.rigthKey
                ) io.send_event("stop");

            },

            create: function() {

                this.loadImage("beam", "rock", "floor", "p_1_down", "p_1_left", "p_1_right", "p_1_up", "p_2_down", "p_2_left", "p_2_right", "p_2_up", "bomb", "explosion", "B", "M", "P","S", "H"); //Incassable, Cassable, Sol

            },

            ready: function() {

                /*
                 ready event listener - if you want to do something
                 when loader has finished the job
                 */

            },

            render: function() {

                this.layer.clear("#ffffff");

                var map = io.map;
                var players = io.players;
                var bombs = io.bombs;
                var explosions = io.explosions;
                var powerups = io.powerups;


                for (var x in io.map) { // Rendu de la map à partir de l'Array 2D
                    for (var y in io.map[x]) {
                        //console.log(ligne, colonne);
                        if (io.map[x][y] == "#") this.layer.drawImage(this.images.rock, x * 40, y * 40);
                        else if (io.map[x][y] == "&") this.layer.drawImage(this.images.beam, x * 40, y * 40);
                        else if (io.map[x][y] == " ") this.layer.drawImage(this.images.floor, x * 40, y * 40);
                    }
                }

                for (var player in Object.keys(players)) {
                    switch (players[Object.keys(players)[player]].direction) {
                        case "N": this.layer.drawImage(this.images["p_" + (parseInt(player) + 1) + "_up"], players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20)
                            break;
                        case "S": this.layer.drawImage(this.images["p_" + (parseInt(player) + 1) + "_down"], players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20)
                            break;
                        case "E": this.layer.drawImage(this.images["p_" + (parseInt(player) + 1) + "_right"], players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20)
                            break;
                        case "W": this.layer.drawImage(this.images["p_" + (parseInt(player) + 1) + "_left"], players[Object.keys(players)[player]].position[0] * 40 - 20, players[Object.keys(players)[player]].position[1] * 40 - 20)
                            break;
                    }
                }

                for (var bomb in bombs) {
                    this.layer.drawImage(this.images["bomb"], bombs[bomb].position[0] * 40 - 20, bombs[bomb].position[1] * 40 - 20, 40, 40);
                }

                for (var explosion in explosions) {
                    this.layer.drawImage(this.images["explosion"], explosions[explosion].position[0] * 40 - 20, explosions[explosion].position[1] * 40 - 20);
                    setTimeout(this.layer.drawImage(this.images["floor"], explosions[explosion].position[0] * 40 - 20, explosions[explosion].position[1] * 40 - 20), 1000);
                    for (var powerup in powerups) {
                        this.layer.drawImage(this.image[powerup], powerups[powerup][0] * 40 - 20, powerups[powerup][1] * 40 - 20, 40, 40);
                        setTimeout(this.layer.drawImage(this.images["floor"], explosions[explosion].position[0] * 40 - 20, explosions[explosion].position[1] * 40 - 20), 1000);
                    }
                }


            }

        })

        // ------------------------------------------------------------------------------------------------------------------ //

        // Nouveau IO => Gère la communication client - serveur //

        io = new IO("localhost", 28456, this.game_name.value, app);

        // -------------------------------------------------------- //

    }); // Fin de la fonction onsubmit

} // Fin du main()
