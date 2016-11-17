var socket;
var render_interval;
var canvas;

var keysdown = new Set();
var keymap = {
	moveUp: "z",
	moveLeft: "q",
	moveDown: "s",
	moveRight: "d"
};
var angles = {
	moveRight: 0,
	moveUp: Math.PI / 2,
	moveLeft: Math.PI,
	moveDown: Math.PI / 2 * 3
}

function init() {
	socket = new IO("ws://localhost:28456", "robotwar", bluePrint => {
		canvas = document.getElementById("canvas");
		canvas.width = bluePrint.get("size")[0];
		canvas.height = bluePrint.get("size")[1];
		render_interval = setInterval(render, 1000)
	});
	document.body.addEventListener("keydown", event => {
		let char = event.char || event.key
		if (_.chain(keymap).values().contains(char)) {
			if (! keysdown.has(char) ) {
				keysdown.add(char);
				update_movement();
			}	
		}
	});
	document.body.addEventListener("keyup", event => {
		let char = event.char || event.key
		if (keysdown.has(char)) {
			keysdown.delete(char);
			update_movement();
		}
	})
}


function update_movement() {
	var point = {x:0, y:0};

	console.log(keysdown)
	_.chain(keymap).pairs().each(pair => console.log(pair)).filter(
		pair => pair[0].includes("move") && keysdown.has(pair[1])
	).map(
		pair => angles[pair[0]]
	).each(
		angle => {
			point.x += Math.cos(angle);
			point.y += Math.sin(angle);
		}
	)

	if (point.x == 0 && point.y == 0) {
		socket.sendEvent("event_stop_moving", {})
	} else if (point.x == 0) {
		socket.sendEvent("event_move", {direction: (point.y > 0) ? angles["moveUp"] : angles["moveDown"]});
	} else if (point.y == 0) {
		socket.sendEvent("event_move", {direction: (point.x > 0) ? angles["moveRight"] : angles["moveLeft"]});
	} else {
		socket.sendEvent("event_move", {direction: Math.atan(point.y / point.x) + (point.x < 0) ? Math.PI : 0});
	}
}

function render() {
	var bluePrint = socket.getBluePrint();

	var ctx = canvas.getContext("2d");

	ctx.clearRect(0, 0, canvas.width, canvas.height);
	for (let [robot_id, robot] of bluePrint.get("robots").entries()) {
		ctx.beginPath();
		ctx.lineWidth="2";
		ctx.arc(robot.get("position")[0], robot.get("position")[1], robot.get("size"), 0, 2 * Math.PI)
		ctx.fillStyle = (robot_id == socket.id) ? "green" : "red";
		ctx.fill();
		ctx.beginPath();
		ctx.lineWidth="5";
		ctx.fillStyle = "white";
		ctx.moveTo(robot.get("position")[0], robot.get("position")[1])
		ctx.lineTo(robot.get("position")[0] + Math.cos(robot.get("direction")) * robot.get("size"), 
			       robot.get("position")[1] + Math.sin(robot.get("direction")) * robot.get("size"));
		ctx.fill();
	}
}
