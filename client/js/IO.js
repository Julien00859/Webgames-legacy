class IO {
    //var this = this;
    constructor(address, port, game, phaser) {
      this.ws = new WebSocket("ws://" + address + ":" + port);
      this.map = {}
      this.players = {}
      this.bombs = {}
      this.explosions = {}
      this.powerups = {}
      this.id;

      this.ws.onopen = () => {
          console.log("[ws open]");
          this.ws.send(JSON.stringify({cmd: "join_queue", queue: game}));
      }

      this.ws.onclose = () => {
              console.log("[ws close]");
      }

      this.ws.onerror = (e) => {
          console.log("[ws error]");
          console.log(e);
      }

      this.ws.onmessage = (e) => {
          //console.log("[ws message]");
          let data = JSON.parse(e.data);
          //console.log(data);

          switch(data.cmd) {
              case "connection_success":
                  this.id = data.id;
                  console.log(this.id);
                  break;
              case "startup_status":
                  this.map = data.map;
                  this.players = data.players;
                  break;
              case "status":

                  if (data.status.winner) console.log("Le joueur " + data.status.winner + " a gagné !"); // Gagné

                  for (var i in data.status.entities) {
                      if (data.status.entities[i].name == "<Player>") { // Joueur ?
                          if (data.status.entities[i].ismoving) {
                              this.players[this.id] = data.status.entities[i]; // Met à jour la position
                          }

                          else if (data.status.explosions) { // Explosion
                              for (var i in data.status.explosions) {
                                  this.explosions = data.status.explosions; // Met à jour les explosions
                              }
                              this.powerups = data.status.map; // Et les powerups
                          }
                      }

                      else if (data.status.entities[i].name == "<Bomb>") // Bombe
                          this.bombs[i] = data.status.entities[i]; // Met à jour les bombes

                  }
                  break;

          }
      }

    } // Fin Constructeur

    send_event (event, kwargs=undefined) {
        if (kwargs === undefined) kwargs = {};

        this.send_raw({
            cmd: "event",
            event: event,
            kwargs: kwargs
        })
    }

    send_raw (obj) {
        this.ws.send(JSON.stringify(obj))
    };

}
