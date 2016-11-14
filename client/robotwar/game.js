var socket;
var client_id;
var token;
var robot_size;
var robots = {};
var bullets = {};
var size;

var keys = {
	right: {
		char: "d",
		pressed: false,
		angle: 0
	},
	up: {
		char: "z",
		pressed: false,
		angle: Math.PI / 2
	},
	left: {
		char: "q",
		pressed: false,
		angle: Math.PI
	},
	down: {
		char: "s",
		pressed: false,
		angle: Math.PI / 2 * 3
	}
}

function init() {
	socket = new WebSocket("ws://localhost:28456")
	socket.onopen = function() {
		console.log("Connected");
		socket.send(JSON.stringify({cmd: "join_queue", queue: "robotwar"}));
	}
	socket.onclose = function() {
		disableKeys();
		console.log("Disconnected");
	}
	socket.onmessage = function(message) {
		console.log(message);
		data = JSON.parse(message.data);
		switch(data.cmd) {
			case "connection_success":
				token = data.token;
				client_id = data.id;
				break;

			case "startup_status":
				ableKeys();
				robot_size = data.robot_size;
				robots = data.robots
				size = data.size
				break;

			case "status":
				if ("robots" in data) {
					for (var robot in data.robots) {
						if (data.robots[robot].isAlive)
							self.robots[robot] = data.robots[robot];
						else
							delete self.robots[robot]
					}
				}
				if ("bullets" in data) {
					for (var bullet in data.bullets) {
						if (data.bullet.isAlive)
							self.bullets[bullet] = data.bullets[bullet];
						else
							delete self.bullets[bullet];
					}
				}
				break;
		}
		socket.onerror = function(message) {
			console.log(message);
		}
		socket.sendEvent = function(event, kwargs) {
			this.send(JSON.stringify({cmd: "event", event: event, kwargs: (kwargs != void 0) ? kwargs : {}}))
		}
	}
}

function get_keys(event, pressed) {
	if (event.char == keys.up.char1)
		keys.up.pressed = pressed;
	else if (event.char == keys.left.char)
		keys.left.pressed = pressed;
	else if (event.char == keys.down.char)
		keys.down.pressed = pressed;
	else if (event.char == keys.right.char)
		keys.right.pressed = pressed;
}

function sign(x) {
	return x / Math.abs(x)
}

function update_movement() {
	var point = {x:0, y:0};
	Object.keys(keys).filter(function(k) {
		return keys[k].pressed;
	}).map(function(k) {
		return keys[k].angle;
	}).forEach(function(a) {
		point.x += Math.cos(a);
		point.y += Math.sin(a);
	});
	if (point.x == 0 && point.y ==0) {
		socket.sendEvent("event_stop_moving", {})
	} else if (point.x == 0) {
		socket.sendEvent("event_move", {direction: point.y * sign(point.y)});
	} else if (point.y == 0) {
		socket.sendEvent("event_move", {direction: point.x * sign(point.x)});
	} else {
		if (sign(point.x) == sign(point.y)) {
			socket.sendEvent("event_move", {direction: Math.atan(point.y / point.x) * sign(point.x)});
		} else {
			socket.sendEvent("event_move", {direction: Math.atan(point.y / point.x) * sign(point.x)});
		}
	}
}

function ableKeys() {
	document.body.addEventListener("keydown", function(event){
		console.log("Event!");
		get_keys(event, true)
		update_movement()
	});
	document.body.addEventListener("keyup", function(event){
		console.log("Event!");
		get_keys(event, false)
		update_movement()
	});
}