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

            create: function() {

                this.loadImage("beam", "rock", "floor" ); //Incassable, Cassable, Sol

            },

            ready: function() {

                /*
                 ready event listener - if you want to do something
                 when loader has finished the job
                 */

            },

            render: function() {

                this.layer.clear("#ffffff");
                this.layer.drawImage(this.images.rock, (2 * 40), (2 * 40));
                this.layer.drawImage(this.images.rock, 40, 40);
                this.layer.drawImage(this.images.rock, 0, 0);

                //map = io.map;
                for (var ligne in io.map) { // Rendu de la map à partir de l'Array 2D
                    for (var colonne in io.map[ligne]) {
                        //console.log(ligne, colonne);
                        if (io.map[ligne][colonne] == "#") this.layer.drawImage(this.images.rock, (colonne * 40), (ligne * 40));
                        else if (io.map[ligne][colonne] == "&") this.layer.drawImage(this.images.beam, colonne * 40, ligne * 40);
                        else if (io.map[ligne][colonne] == " ") this.layer.drawImage(this.images.floor, colonne * 40, ligne * 40);
                    }
                }

            }

        })

        // ------------------------------------------------------------------------------------------------------------------ //

        // Nouveau IO => Gère la communication client - serveur //

        io = new IO("localhost", 28456, this.game_name.value, app);

        // -------------------------------------------------------- //

        // Ecoute les touches

        document.getElementById("game").addEventListener("keydown", function(event){
            if      (event.key == config.upKey)     io.send_event("move", ["N"]);
            else if (event.key == config.downKey)   io.send_event("move", ["S"]);
            else if (event.key == config.leftKey)   io.send_event("move", ["W"]);
            else if (event.key == config.rigthKey)  io.send_event("move", ["E"]);
            else if (event.key == config.plantKey)  io.send_event("plant");
            else if (event.key == config.fuseKey)   io.send_event("fuse");
        });

        document.getElementById("game").addEventListener("keyup", function(event){
            if (
                event.key == config.upKey ||
                event.key == config.downKey ||
                event.key == config.leftKey ||
                event.key == config.rigthKey
            ) io.send_event("stop");
        });

        // ------------------------------------------------------------------------ //


    }); // Fin de la fonction onsubmit

} // Fin du main()


