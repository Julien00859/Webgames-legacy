var IO = function IO(address, port, game, phaser) {
    var self = this;

    self.ws = new WebSocket("ws://" + address + ":" + port);

    self.map = {}
    self.players = {}
    self.bombs = {}
    self.explosions = {}
    self.powerups = {}
    self.id;

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
        //console.log("[ws message]");
        var data = JSON.parse(e.data);
        //console.log(data);

        switch(data.cmd) {
            case "connection_success":
                self.id = data.id;
                break;
            case "startup_status":
                //console.log(data.map);
                self.map = data.map;
                self.players = data.players;
                //playground.render();
                break;
            case "status":

                if (data.status.winner) console.log("Le joueur " + data.status.winner + " a gagné !"); // Gagné

                for (var i in data.status.entities) {
                    if (data.status.entities[i].name == "<Player>") { // Joueur ?
                        if (data.status.entities[i].ismoving) {
                            self.players[self.id] = data.status.entities[i]; // Met à jour la position
                        }

                        else if (data.status.explosions) { // Explosion
                            for (var i in data.status.explosions) {
                                self.explosions = data.status.explosions; // Met à jour les explosions
                            }
                            self.powerups = data.status.map; // Et les powerups
                        }
                    }

                    else if (data.status.entities[i].name == "<Bomb>") // Bombe
                        self.bombs[i] = data.status.entities[i]; // Met à jour les bombes

                }
                break;

        }

    }
}

IO.prototype.send_event = function send_event(event, kwargs=undefined) {
    if (kwargs === undefined) kwargs = {};

    this.send_raw({
        cmd: "event",
        event: event,
        kwargs: kwargs
    })
}

IO.prototype.send_raw = function(obj) {
    this.ws.send(JSON.stringify(obj))
};


