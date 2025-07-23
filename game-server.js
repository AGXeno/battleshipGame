const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const io = require('socket.io')(server);
const path = require('path');

// Serve static files
app.use(express.static(__dirname));

// Game state management
class GameRoom {
    constructor(roomId) {
        this.roomId = roomId;
        this.players = new Map();
        this.gameState = {
            ships: [],
            cannonballs: [],
            obstacles: [],
            scores: {
                team1: 0,
                team2: 0
            },
            gameStarted: false,
            gameStartTime: null,
            nextShipId: 1,
            nextCannonballId: 1
        };
        this.lastUpdate = Date.now();
        this.generateObstacles();
    }

    addPlayer(socketId, playerData) {
        const team = this.players.size === 0 ? 'team1' : 'team2';
        this.players.set(socketId, {
            id: socketId,
            team: team,
            ready: false,
            ...playerData
        });
        return team;
    }

    removePlayer(socketId) {
        // Remove player's ships
        this.gameState.ships = this.gameState.ships.filter(ship => ship.ownerId !== socketId);
        this.players.delete(socketId);
    }

    generateObstacles() {
        // Islands
        for (let i = 0; i < 2; i++) {
            this.gameState.obstacles.push({
                id: `island_${i}`,
                type: 'island',
                x: 250 + Math.random() * 500,
                y: 150 + Math.random() * 400,
                radius: 30 + Math.random() * 20,
                destructible: false
            });
        }
        
        // Icebergs
        for (let i = 0; i < 3; i++) {
            this.gameState.obstacles.push({
                id: `iceberg_${i}`,
                type: 'iceberg',
                x: 150 + Math.random() * 700,
                y: 100 + Math.random() * 500,
                radius: 20 + Math.random() * 15,
                destructible: true,
                health: 3
            });
        }
    }

    startGame() {
        this.gameState.gameStarted = true;
        this.gameState.gameStartTime = Date.now();
        
        // Spawn initial ships for each team
        const spawnPoints = {
            team1: { x: 100, y: 620 },
            team2: { x: 900, y: 80 }
        };
        
        // Schedule ship spawns
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                if (this.gameState.gameStarted) {
                    for (const [playerId, player] of this.players) {
                        this.spawnShip(playerId, player.team, spawnPoints[player.team]);
                    }
                }
            }, i * 3000);
        }
    }

    spawnShip(ownerId, team, spawnPoint) {
        const angle = team === 'team1' ? -45 * Math.PI/180 : 135 * Math.PI/180;
        const ship = {
            id: `ship_${this.nextShipId++}`,
            ownerId: ownerId,
            team: team,
            x: spawnPoint.x + (Math.random() - 0.5) * 60,
            y: spawnPoint.y + (Math.random() - 0.5) * 60,
            angle: angle,
            rudderAngle: 0,
            targetRudderAngle: 0,
            cannonAngle: angle,
            speed: 25,
            health: 3,
            maxHealth: 3,
            lastShot: Date.now(),
            shotCooldown: 5000,
            spawnTime: Date.now()
        };
        
        this.gameState.ships.push(ship);
        return ship;
    }

    updateShipControl(playerId, shipId, controlData) {
        const ship = this.gameState.ships.find(s => s.id === shipId && s.ownerId === playerId);
        if (ship) {
            if (controlData.targetRudderAngle !== undefined) {
                ship.targetRudderAngle = Math.max(-Math.PI/4, Math.min(Math.PI/4, controlData.targetRudderAngle));
            }
            if (controlData.cannonAngle !== undefined) {
                ship.cannonAngle = controlData.cannonAngle;
            }
        }
    }

    update(deltaTime) {
        if (!this.gameState.gameStarted) return;

        // Update ships
        for (const ship of this.gameState.ships) {
            // Update rudder
            const rudderSpeed = 2.0;
            const rudderDiff = ship.targetRudderAngle - ship.rudderAngle;
            ship.rudderAngle += Math.sign(rudderDiff) * Math.min(Math.abs(rudderDiff), rudderSpeed * deltaTime);
            
            // Update angle and position
            const turnRate = 0.8;
            ship.angle += ship.rudderAngle * turnRate * deltaTime;
            
            ship.x += Math.cos(ship.angle) * ship.speed * deltaTime;
            ship.y += Math.sin(ship.angle) * ship.speed * deltaTime;
            
            // Boundary collision with bounce
            if (ship.x < 0 || ship.x > 1000) {
                ship.x = Math.max(0, Math.min(1000, ship.x));
                ship.angle = Math.PI - ship.angle;
                ship.rudderAngle = 0;
                ship.targetRudderAngle = 0;
            }
            
            if (ship.y < 0 || ship.y > 700) {
                ship.y = Math.max(0, Math.min(700, ship.y));
                ship.angle = -ship.angle;
                ship.rudderAngle = 0;
                ship.targetRudderAngle = 0;
            }
            
            // Auto-fire cannons
            const timeSinceSpawn = Date.now() - ship.spawnTime;
            const timeSinceLastShot = Date.now() - ship.lastShot;
            
            if (timeSinceSpawn >= 5000 && timeSinceLastShot >= ship.shotCooldown) {
                this.fireCannonball(ship);
            }
        }

        // Update cannonballs
        for (const cannonball of this.gameState.cannonballs) {
            cannonball.x += Math.cos(cannonball.angle) * cannonball.speed * deltaTime;
            cannonball.y += Math.sin(cannonball.angle) * cannonball.speed * deltaTime;
            
            // Remove out of bounds cannonballs
            if (cannonball.x < -10 || cannonball.x > 1010 || 
                cannonball.y < -10 || cannonball.y > 710) {
                cannonball.dead = true;
            }
        }

        // Check collisions
        this.checkCollisions();

        // Clean up dead objects
        this.gameState.ships = this.gameState.ships.filter(s => s.health > 0);
        this.gameState.cannonballs = this.gameState.cannonballs.filter(c => !c.dead);
        this.gameState.obstacles = this.gameState.obstacles.filter(o => !o.dead);

        // Check win conditions
        if (this.gameState.scores.team1 >= 15 || this.gameState.scores.team2 >= 15) {
            this.gameState.gameStarted = false;
        }
    }

    fireCannonball(ship) {
        const cannonball = {
            id: `cannonball_${this.nextCannonballId++}`,
            shooterId: ship.id,
            shooterTeam: ship.team,
            x: ship.x + Math.cos(ship.cannonAngle) * 25,
            y: ship.y + Math.sin(ship.cannonAngle) * 25,
            angle: ship.cannonAngle,
            speed: 150,
            dead: false
        };
        
        this.gameState.cannonballs.push(cannonball);
        ship.lastShot = Date.now();
    }

    checkCollisions() {
        // Ship-obstacle collisions
        for (const ship of this.gameState.ships) {
            for (const obstacle of this.gameState.obstacles) {
                const dx = ship.x - obstacle.x;
                const dy = ship.y - obstacle.y;
                const distance = Math.sqrt(dx*dx + dy*dy);
                
                if (distance < obstacle.radius + 12) {
                    ship.health -= 0.01;
                    const pushX = (dx / distance) * 2;
                    const pushY = (dy / distance) * 2;
                    ship.x += pushX;
                    ship.y += pushY;
                }
            }
        }

        // Cannonball-ship collisions
        for (const cannonball of this.gameState.cannonballs) {
            for (const ship of this.gameState.ships) {
                if (cannonball.shooterTeam === ship.team) continue;
                
                const dx = cannonball.x - ship.x;
                const dy = cannonball.y - ship.y;
                const distance = Math.sqrt(dx*dx + dy*dy);
                
                if (distance < 15) {
                    cannonball.dead = true;
                    ship.health -= 1;
                    
                    if (ship.health <= 0) {
                        this.gameState.scores[cannonball.shooterTeam]++;
                        // Respawn ship after delay
                        const team = ship.team;
                        const ownerId = ship.ownerId;
                        const spawnPoint = team === 'team1' ? { x: 100, y: 620 } : { x: 900, y: 80 };
                        setTimeout(() => {
                            if (this.gameState.gameStarted) {
                                this.spawnShip(ownerId, team, spawnPoint);
                            }
                        }, 3000);
                    }
                }
            }
        }

        // Cannonball-obstacle collisions
        for (const cannonball of this.gameState.cannonballs) {
            for (const obstacle of this.gameState.obstacles) {
                const dx = cannonball.x - obstacle.x;
                const dy = cannonball.y - obstacle.y;
                const distance = Math.sqrt(dx*dx + dy*dy);
                
                if (distance < obstacle.radius + 3) {
                    cannonball.dead = true;
                    
                    if (obstacle.destructible) {
                        obstacle.health--;
                        obstacle.radius -= 5;
                        if (obstacle.health <= 0 || obstacle.radius <= 10) {
                            obstacle.dead = true;
                        }
                    }
                }
            }
        }
    }

    getState() {
        return {
            ...this.gameState,
            playerCount: this.players.size,
            players: Array.from(this.players.values())
        };
    }
}

// Store active game rooms
const gameRooms = new Map();

// Game update loop
setInterval(() => {
    const now = Date.now();
    for (const [roomId, room] of gameRooms) {
        const deltaTime = (now - room.lastUpdate) / 1000;
        room.lastUpdate = now;
        room.update(deltaTime);
        
        // Broadcast updated state to all players in room
        io.to(roomId).emit('game-state', room.getState());
    }
}, 1000 / 60); // 60 FPS

// Socket.io connection handling
io.on('connection', (socket) => {
    console.log('Player connected:', socket.id);
    
    socket.on('join-room', (roomId) => {
        // Leave any existing rooms
        for (const room of socket.rooms) {
            if (room !== socket.id) {
                socket.leave(room);
                const gameRoom = gameRooms.get(room);
                if (gameRoom) {
                    gameRoom.removePlayer(socket.id);
                    if (gameRoom.players.size === 0) {
                        gameRooms.delete(room);
                    }
                }
            }
        }
        
        // Join new room
        socket.join(roomId);
        
        // Get or create game room
        if (!gameRooms.has(roomId)) {
            gameRooms.set(roomId, new GameRoom(roomId));
        }
        
        const gameRoom = gameRooms.get(roomId);
        const team = gameRoom.addPlayer(socket.id);
        
        socket.emit('joined-room', {
            roomId: roomId,
            playerId: socket.id,
            team: team,
            gameState: gameRoom.getState()
        });
        
        socket.to(roomId).emit('player-joined', {
            playerId: socket.id,
            playerCount: gameRoom.players.size
        });
        
        console.log(`Player ${socket.id} joined room ${roomId} as ${team}`);
    });
    
    socket.on('start-game', (roomId) => {
        const gameRoom = gameRooms.get(roomId);
        if (gameRoom && !gameRoom.gameState.gameStarted) {
            gameRoom.startGame();
            io.to(roomId).emit('game-started', {
                gameStartTime: gameRoom.gameState.gameStartTime
            });
        }
    });
    
    socket.on('ship-control', (data) => {
        const gameRoom = gameRooms.get(data.roomId);
        if (gameRoom) {
            gameRoom.updateShipControl(socket.id, data.shipId, data.control);
        }
    });
    
    socket.on('disconnect', () => {
        console.log('Player disconnected:', socket.id);
        
        // Remove from all game rooms
        for (const [roomId, gameRoom] of gameRooms) {
            if (gameRoom.players.has(socket.id)) {
                gameRoom.removePlayer(socket.id);
                
                socket.to(roomId).emit('player-left', {
                    playerId: socket.id,
                    playerCount: gameRoom.players.size
                });
                
                // Clean up empty rooms
                if (gameRoom.players.size === 0) {
                    gameRooms.delete(roomId);
                }
            }
        }
    });
});

const PORT = process.env.PORT || 3001;
const HOST = process.env.HOST || '0.0.0.0'; // Accept connections from any IP

server.listen(PORT, HOST, () => {
    console.log(`Game server running on http://${HOST}:${PORT}`);
    console.log(`Local access: http://localhost:${PORT}/naval_battle_server.html`);
    console.log(`Network access: http://[YOUR_IP_ADDRESS]:${PORT}/naval_battle_server.html`);
    console.log('\nTo find your IP address:');
    console.log('  Windows: ipconfig');
    console.log('  Mac/Linux: ifconfig or ip addr show');
});