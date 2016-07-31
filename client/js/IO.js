var IO = function IO(address, port, game, playground) {
    var self = this;

    self.ws = new WebSocket("ws://" + address + ":" + port);

    self.map = {}
    self.players = {}

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
            self.map = data.map;
            self.players = data.players;
            playground.render();
        }

    }
}

IO.prototype.send_event = function send_event(event, args=undefined, kwargs=undefined) {
    if (args === undefined) args = [];
    if (kwargs === undefined) kwargs = {};

    this.send_raw({
        cmd: "event",
        event: event,
        args: args,
        kwargs: kwargs
    }) 
}

IO.prototype.send_raw = function(obj) {
    this.ws.send(JSON.stringify(obj))
};