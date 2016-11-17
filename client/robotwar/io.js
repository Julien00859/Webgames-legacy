class IO {
	constructor(address, queueToJoin, callback) {
		this.id = undefined;
		this.token = undefined;
		this.bluePrint = new Map();
		this.queueToJoin = queueToJoin;
		this.callback = callback;

		this._ws = new WebSocket(address);
		this._ws.io = this;
		this._ws.onopen = this.onopen;
		this._ws.onmessage = this.onmessage;
		this._ws.onerror = this.onerror;
		this._ws.onclose = this.onclose;
	}

	onopen(event) {
		console.log(event);
	}

	onmessage(event) {
		let data = JSON.parse(event.data);
		console.log(data)
		switch (data.cmd) {
			case "connection_success":
				this.io.id = data.id;
				this.io.token = data.token;
				this.io.joinQueue(this.io.queueToJoin);
				break

			case "startup_status":
				objectToMap(data.startup_status, this.io.bluePrint);
				this.io.callback(this.io.bluePrint)
				break;

			case "status":
				objectToMap(data.status, this.io.bluePrint);
				break;


		}
	}

	onclose(event) {
		console.log(event);
	}

	onerror(event) {
		console.log(event);
	}

	getBluePrint() {
		return this.bluePrint;
	}

	send(object) {
		console.log(object);
		this._ws.send(JSON.stringify(object));
	}

	sendEvent(event, kwargs) {
		this.send({cmd: "event", event, kwargs});
	}

	joinQueue(queue) {
		this.send({cmd: "join_queue", queue});
	}
}


function objectToMap(object, map) {
	for (let pair of _.pairs(object)) {
		if (_.isObject(pair[1]) && !_.isArray(pair[1])) {
			let nextMap;
			if (map.has(pair[0])) {
				nextMap = map.get(pair[0]);
			} else {
				nextMap = new Map();
				map.set(pair[0], nextMap)
			}
			objectToMap(pair[1], nextMap);
		} else {
			map.set(pair[0], pair[1]);
		}
	}
}