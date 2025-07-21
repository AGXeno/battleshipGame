const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Store active rooms
const rooms = new Map();

io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);

  // Handle room creation
  socket.on('create-room', (callback) => {
    const roomId = Math.random().toString(36).substr(2, 9);
    rooms.set(roomId, {
      players: [socket.id],
      host: socket.id
    });
    socket.join(roomId);
    socket.roomId = roomId;
    callback({ roomId });
    console.log(`Room ${roomId} created by ${socket.id}`);
  });

  // Handle joining room
  socket.on('join-room', (roomId, callback) => {
    const room = rooms.get(roomId);
    if (!room) {
      callback({ error: 'Room not found' });
      return;
    }
    if (room.players.length >= 2) {
      callback({ error: 'Room is full' });
      return;
    }
    
    room.players.push(socket.id);
    socket.join(roomId);
    socket.roomId = roomId;
    
    // Notify the other player
    socket.to(roomId).emit('player-joined', { playerId: socket.id });
    callback({ success: true, players: room.players });
    console.log(`Player ${socket.id} joined room ${roomId}`);
  });

  // Handle WebRTC signaling
  socket.on('offer', (data) => {
    socket.to(data.to).emit('offer', {
      from: socket.id,
      offer: data.offer
    });
  });

  socket.on('answer', (data) => {
    socket.to(data.to).emit('answer', {
      from: socket.id,
      answer: data.answer
    });
  });

  socket.on('ice-candidate', (data) => {
    socket.to(data.to).emit('ice-candidate', {
      from: socket.id,
      candidate: data.candidate
    });
  });

  // Handle game state updates
  socket.on('game-state', (data) => {
    if (socket.roomId) {
      socket.to(socket.roomId).emit('game-state', data);
    }
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    if (socket.roomId) {
      const room = rooms.get(socket.roomId);
      if (room) {
        room.players = room.players.filter(id => id !== socket.id);
        if (room.players.length === 0) {
          rooms.delete(socket.roomId);
          console.log(`Room ${socket.roomId} deleted`);
        } else {
          socket.to(socket.roomId).emit('player-disconnected', { playerId: socket.id });
        }
      }
    }
  });
});

server.listen(PORT, () => {
  console.log(`WebRTC signaling server running on port ${PORT}`);
});