var IO = function IO(address, port, game, playground) {
    var self = this;

    self.ws = new WebSocket("ws://" + address + ":" + port);

    self.map = {}

    self.ws.onopen = function() {
        console.log("[ws open]");
        self.ws.send(JSON.stringify({cmd: "join_queue", queue: game}));
    }

    self.ws.onclose = function() {
            console.log("[ws close]");
    }

    self.ws.onerror = function(e) {
        console.log("[ws error]");
        console.log(e);
    }

    self.ws.onmessage = function(e) {
        console.log("[ws message]");
        var data = JSON.parse(e.data);
        console.log(data);

        if (data.cmd == "startup_status") { // Démarrage du jeu
            console.log(data.map);
            /*var map = []; // Array 2D
            var mapping = []; // Une ligne de l'Array (construite à partir du string (data.map))
            for (var i in data.map) { // Fonction qui construit l'Array 2D
                if (data.map[i] == "\n") {
                    map.push(mapping)
                    mapping = []
                } else mapping.push(data.map[i])
            }*/
            // console.log(map);
            /*for (var ligne in map) { // Rendu de la map à partir de l'Array 2D
                for (var colonne in map[ligne]) {
                    console.log(ligne, colonne)
                    if (map[ligne][colonne] == "#") this.layer.drawImage(this.images.rock, colonne * 40, ligne * 40);
                    if (map[ligne][colonne] == "&") this.layer.drawImage(this.images.beam, colonne * 40, ligne * 40);
                    if (map[ligne][colonne] == " ") this.layer.drawImage(this.images.floor, colonne * 40, ligne * 40);
                }
            }*/
            playground.render(data.map);
            self.map = data.map;
            console.log(self.map)
        }

    }
}

IO.prototype.send_event = function send_event(event, args=undefined, kwargs=undefined) {
    if (args === undefined) args = [];
    if (kwargs === undefined) kwargs = {};

    self.send_raw({
        cmd: "event",
        event: event,
        args: args,
        kwargs: kwargs
    }) 
}

IO.prototype.send_raw = function(obj) {
    self.ws.send(JSON.stringify(obj))
};