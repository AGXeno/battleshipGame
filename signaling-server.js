const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const io = require('socket.io')(server);
const path = require('path');

// Serve static files (including naval_battle.html)
app.use(express.static(__dirname));

// Track rooms and players
const rooms = new Map();

io.on('connection', (socket) => {
    console.log('User connected:', socket.id);
    
    // Join room
    socket.on('join-room', (roomId) => {
        // Leave any existing rooms
        for (const room of socket.rooms) {
            if (room !== socket.id) {
                socket.leave(room);
            }
        }
        
        // Join the new room
        socket.join(roomId);
        
        // Get or create room info
        if (!rooms.has(roomId)) {
            rooms.set(roomId, new Set());
        }
        const room = rooms.get(roomId);
        room.add(socket.id);
        
        // Determine if this player is the host (first player in room)
        const isHost = room.size === 1;
        
        // Get existing players in room (for WebRTC connection)
        const existingPlayers = Array.from(room).filter(id => id !== socket.id);
        
        // Notify the joining player
        socket.emit('joined-room', {
            roomId: roomId,
            playerId: socket.id,
            playerCount: room.size,
            isHost: isHost,
            existingPlayers: existingPlayers
        });
        
        // Notify other players in the room
        socket.to(roomId).emit('player-joined', {
            playerId: socket.id,
            playerCount: room.size
        });
        
        console.log(`User ${socket.id} joined room ${roomId}. Room now has ${room.size} players.`);
    });
    
    // WebRTC signaling
    socket.on('offer', (data) => {
        console.log('Relaying offer from', socket.id, 'to', data.to);
        socket.to(data.to).emit('offer', {
            from: socket.id,
            offer: data.offer
        });
    });
    
    socket.on('answer', (data) => {
        console.log('Relaying answer from', socket.id, 'to', data.to);
        socket.to(data.to).emit('answer', {
            from: socket.id,
            answer: data.answer
        });
    });
    
    socket.on('ice-candidate', (data) => {
        console.log('Relaying ICE candidate from', socket.id, 'to', data.to);
        socket.to(data.to).emit('ice-candidate', {
            from: socket.id,
            candidate: data.candidate
        });
    });
    
    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        
        // Remove from all rooms
        for (const [roomId, players] of rooms.entries()) {
            if (players.has(socket.id)) {
                players.delete(socket.id);
                
                // Notify other players in the room
                socket.to(roomId).emit('player-left', {
                    playerId: socket.id,
                    playerCount: players.size
                });
                
                // Clean up empty rooms
                if (players.size === 0) {
                    rooms.delete(roomId);
                }
            }
        }
    });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
    console.log(`Signaling server running on http://localhost:${PORT}`);
    console.log(`Open http://localhost:${PORT}/naval_battle.html in your browser`);
});