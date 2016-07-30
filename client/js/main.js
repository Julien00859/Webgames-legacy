config = {
    upKey: "z",
    downKey: "s",
    leftKey: "q",
    rigthKey: "d",
    plantKey: "o",
    fuseKey: "p"
}

io = new IO("localhost", 28456);

function main() {

    document.getElementById("game").addEventListener("focus", function(){
        console.log("focus");
    });

    document.getElementById("game").addEventListener("blur", function(){
        console.log("blur");
    });

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
        event.preventDefault();
        io.send_raw({cmd: "join_queue", queue: this.game_name.value})

        io.ws.onmessage(function(e){
            console.log('msg');
            var data = e.data;

            if (data.cmd == "startup_status") { // Démarrage du jeu
                console.log('start');
                console.log(data);
            }
        })

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

                this.layer.clear("#ffffff")
                this.layer.drawImage(this.images.floor, 0, 0)

            }

        })
    });


}


