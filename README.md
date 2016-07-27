# Bomberman
Play the game in your browser with friends

# Dependencies

* [Websocket-server](https://github.com/Pithikos/python-websocket-server)

# Server-side `server/`

## `web_server.py`
Manage the connection with the client's browser by handling connections, disconnections and incomming messages.

* Add incommers to the game manager
* Remove outgoers from the game manager
* Syntax check the messages (JSON object to python dictionnary)
* Lexical check the messages (Must follow the exchange protocol)
* Call function following the message content

## `game_manager.py`
Manage players, game queues and games.

* Add or remove players from wait queue
* Start a new game when a queue is full
* Handle each running games with events and message status

# Server-side `game/`

## `bomberman.py`
Manage a bomberman game with multiple player

* Convert a map-file into a game representation
* Handle player's event such as move, stop, plant, fuse, die
* Handle bombs countdown, explions and deflagration
* Compute entities's movement
* Provide a status for each tick containing useful informations such as entities's position, explosion, powerups, ...

## `entities.py`
A class of all the entities used by the bomberman
