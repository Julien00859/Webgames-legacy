var socket;
var render_interval;
var canvas;
var started = false;
var mouse;

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
	canvas = document.getElementById("canvas")

	socket = new IO("ws://localhost:28456", "robotwar", {
		"onstartupstatus": data => {
			canvas.width = socket.getBluePrint().get("size")[0];
			canvas.height = socket.bluePrint.get("size")[1];
			mouse = {
				x: canvas.width / 2,
				y: canvas.height / 2
			}
			render_interval = setInterval(render, 10)
			started = true;
		},
		"onstatus": data => {
			if (socket.getBluePrint().get("robots").get("" + socket.id).get("isMoving")) updateTurretAngle();
		}
	});
	document.body.addEventListener("keydown", event => {
		if (!started) return;

		let char = event.char || event.key
		if (_.chain(keymap).values().contains(char)) {
			if (! keysdown.has(char) ) {
				keysdown.add(char);
				updateMovement();
			}	
		}
	});
	document.body.addEventListener("keyup", event => {
		if (!started) return;

		let char = event.char || event.key
		if (keysdown.has(char)) {
			keysdown.delete(char);
			updateMovement();
		}
	});
	canvas.addEventListener("mousemove", event => {
		if (!started) return;

		if (mouse.x != event.pageX || mouse.y != event.pageY) {
			mouse.x = event.pageX;
			mouse.y = event.pageY;
			updateTurretAngle();	
		}
	});

	canvas.addEventListener("mousedown", event => {
		socket.sendEvent("event_shoot", {});
	});

	canvas.addEventListener("mouseup", event => {
		socket.sendEvent("event_stop_shooting", {});
	});
}

function updateTurretAngle() {
	let position = socket.getBluePrint().get("robots").get(""+socket.id).get("position");
	let point = {
		x: -position[0] + mouse.x,
		y: socket.getBluePrint().get("size")[1] - position[1] - mouse.y
	}

	if (Math.EPSILON <= point.x && point.x <= Math.EPSILON && Math.EPSILON <= point.y && point.y <= Math.EPSILON) {

	} else if (Math.EPSILON <= point.x && point.x <= Math.EPSILON) {
		socket.sendEvent("event_rotate", {angle: (y < 0) ? angles["moveDown"] : angles["moveUp"]});
	} else if (Math.EPSILON <= point.y && point.y <= Math.EPSILON) {
		socket.sendEvent("event_rotate", {angle: (x < 0) ? angles["moveLeft"] : angles["moveRight"]});
	} else {
		socket.sendEvent("event_rotate", {angle: Math.atan(point.y / point.x) + ((point.x < 0) ? Math.PI : 0)});
	}
}


function updateMovement() {

	var point = {x:0, y:0};

	_.chain(keymap).pairs().filter(
		pair => pair[0].includes("move") && keysdown.has(pair[1])
	).map(
		pair => angles[pair[0]]
	).each(
		angle => {
			point.x += Math.cos(angle);
			point.y += Math.sin(angle);
		}
	)

	console.log(point)

	if (-Number.EPSILON <= point.x && point.x <= Number.EPSILON && -Number.EPSILON <= point.y && point.y <= Number.EPSILON) {
		socket.sendEvent("event_stop_moving", {})
	} else if (-Number.EPSILON <= point.x && point.x <= Number.EPSILON) {
		socket.sendEvent("event_move", {direction: (point.y > 0) ? angles["moveUp"] : angles["moveDown"]});
	} else if (-Number.EPSILON <= point.y && point.y <= Number.EPSILON) {
		socket.sendEvent("event_move", {direction: (point.x > 0) ? angles["moveRight"] : angles["moveLeft"]});
	} else {
		socket.sendEvent("event_move", {direction: Math.atan(point.y / point.x) + ((point.x < 0) ? Math.PI : 0)});
	}
}

function render() {
	var bluePrint = socket.getBluePrint();

	var ctx = canvas.getContext("2d");

	ctx.clearRect(0, 0, canvas.width, canvas.height);
	for (let [robot_id, robot] of bluePrint.get("robots").entries()) {
		ctx.beginPath();
		ctx.arc(robot.get("position")[0], bluePrint.get("size")[1] - robot.get("position")[1], robot.get("size"), 0, 2 * Math.PI)
		ctx.fillStyle = (robot_id == socket.id) ? "green" : "red";
		ctx.fill();
		ctx.beginPath();
		ctx.lineWidth = "1";
		ctx.arc(robot.get("position")[0], bluePrint.get("size")[1] - robot.get("position")[1], robot.get("size"), 0, 2 * Math.PI)
		ctx.stroke();
		ctx.beginPath();
		ctx.lineWidth = "5";
		ctx.strokeStyle = '#000000';
		ctx.moveTo(robot.get("position")[0], bluePrint.get("size")[1] - robot.get("position")[1])
		ctx.lineTo(robot.get("position")[0] + Math.cos(robot.get("turretAngle")) * robot.get("size") * 1.2, 
			       bluePrint.get("size")[1] - (robot.get("position")[1] + Math.sin(robot.get("turretAngle")) * robot.get("size") * 1.2));
		ctx.stroke();
	}
	if (bluePrint.has("bullets")) {
		for (let [bullet_id, bullet] of bluePrint.get("bullets").entries()) {
			ctx.beginPath();
			ctx.lineWidth = "3";
			ctx.moveTo(bullet.get("position")[0], bluePrint.get("size")[1] - bullet.get("position")[1])
			ctx.lineTo(bullet.get("position")[0] + Math.cos(bullet.get("direction")) * bullet.get("size"), 
				       bluePrint.get("size")[1] - (bullet.get("position")[1] + Math.sin(bullet.get("direction")) * bullet.get("size")));
			ctx.stroke();
		}	
	}
}
