var socketio = require('socket.io');
var http = require('http');

var server = http.createServer().listen(52273);

var io = socketio().listen(server);
io.sockets.on('connection', (socket) => {
	socket.join("videos");
	socket.on('streaming', (data) => {
		console.log(data);
		io.sockets.in("videos").emit('streaming', data);
	});
});

/*
server.js
*/
