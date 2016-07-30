var IO = function IO(address, port) {
    this.ws = new WebSocket("ws://" + address + ":" + port);

    this.msg = {};


    this.ws.onopen = function() {
        console.log("[ws open]");
    }

    this.ws.onclose = function() {
            console.log("[ws close]");
    }

    this.ws.onerror = function(e) {
        console.log("[ws error]");
        console.log(e);
    }

    this.ws.onmessage = function(e) {
        console.log("[ws message]");
        console.log(e.data);
        this.msg = e.data;
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