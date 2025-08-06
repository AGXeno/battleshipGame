const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const io = require('socket.io')(server);
const path = require('path');

// Serve static files from current directory
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
            neutralShips: [],
            powerUps: [],
            scores: {
                team1: 0,
                team2: 0
            },
            gameStarted: false,
            gameStartTime: null,
            nextShipId: 1,
            nextCannonballId: 1,
            nextNeutralShipId: 1,
            nextPowerUpId: 1,
            lastNeutralSpawn: 0
        };
        this.lastUpdate = Date.now();
        this.generateObstacles();
    }

    addPlayer(socketId, playerData) {
        const isHost = this.players.size === 0;
        const team = this.players.size === 0 ? 'team1' : 'team2';
        this.players.set(socketId, {
            id: socketId,
            team: team,
            ready: false,
            isHost: isHost,
            ...playerData
        });
        return { team, isHost };
    }
    
    togglePlayerReady(socketId) {
        const player = this.players.get(socketId);
        if (player) {
            player.ready = !player.ready;
            return {
                isReady: player.ready,
                allPlayersReady: this.areAllPlayersReady(),
                playerCount: this.players.size
            };
        }
        return null;
    }
    
    areAllPlayersReady() {
        if (this.players.size < 2) return false;
        for (const player of this.players.values()) {
            if (!player.ready) return false;
        }
        return true;
    }

    removePlayer(socketId) {
        // Remove player's ships
        this.gameState.ships = this.gameState.ships.filter(ship => ship.ownerId !== socketId);
        this.players.delete(socketId);
    }

    generateObstacles() {
        // Generate random spawn points on opposite sides of the map
        this.generateRandomSpawnPoints();
        
        // Islands - avoid spawning near team bases (3-5 islands like demo)
        const numIslands = 3 + Math.floor(Math.random() * 3); // 3-5 islands
        for (let i = 0; i < numIslands; i++) {
            let x, y, attempts = 0;
            const minBaseDistance = 150;
            
            do {
                x = 100 + Math.random() * 800; // 10-90% of width (1000px)
                y = 70 + Math.random() * 560; // 10-90% of height (700px)
                attempts++;
                
                // Check distance from both spawn points
                const distToTeam1 = Math.sqrt((x - this.team1SpawnPoint.x) ** 2 + (y - this.team1SpawnPoint.y) ** 2);
                const distToTeam2 = Math.sqrt((x - this.team2SpawnPoint.x) ** 2 + (y - this.team2SpawnPoint.y) ** 2);
                
                // Check distance from existing islands
                let tooCloseToIsland = false;
                for (const existingObstacle of this.gameState.obstacles) {
                    if (existingObstacle.type === 'island') {
                        const dist = Math.sqrt((x - existingObstacle.x) ** 2 + (y - existingObstacle.y) ** 2);
                        if (dist < existingObstacle.radius + 200) { // Minimum spacing
                            tooCloseToIsland = true;
                            break;
                        }
                    }
                }
                
                if (distToTeam1 >= minBaseDistance && distToTeam2 >= minBaseDistance && !tooCloseToIsland) {
                    break; // Good position found
                }
            } while (attempts < 20);
            
            this.gameState.obstacles.push({
                id: `island_${i}`,
                type: 'island',
                x: x,
                y: y,
                radius: 30 + Math.random() * 20,
                destructible: false,
                imageIndex: Math.floor(Math.random() * 6) // 0-5 for 6 island images
            });
        }
        
        // Icebergs (2-5 icebergs like demo)
        const numIcebergs = 2 + Math.floor(Math.random() * 4); // 2-5 icebergs
        for (let i = 0; i < numIcebergs; i++) {
            this.gameState.obstacles.push({
                id: `iceberg_${i}`,
                type: 'iceberg',
                x: 150 + Math.random() * 700,
                y: 100 + Math.random() * 500,
                radius: 20 + Math.random() * 15,
                destructible: true,
                health: 3,
                imageIndex: Math.floor(Math.random() * 12) // 0-11 for 12 iceberg images
            });
        }
    }

    generateRandomSpawnPoints() {
        // Generate two spawn points on opposite sides of the map
        // Choose which sides randomly: corners, edges, or diagonal opposites
        const spawnType = Math.floor(Math.random() * 3);
        
        if (spawnType === 0) {
            // Corner opposites (diagonal)
            if (Math.random() < 0.5) {
                // Top-left vs Bottom-right
                this.team1SpawnPoint = { x: 50 + Math.random() * 100, y: 50 + Math.random() * 100 };
                this.team2SpawnPoint = { x: 850 + Math.random() * 100, y: 550 + Math.random() * 100 };
            } else {
                // Top-right vs Bottom-left
                this.team1SpawnPoint = { x: 850 + Math.random() * 100, y: 50 + Math.random() * 100 };
                this.team2SpawnPoint = { x: 50 + Math.random() * 100, y: 550 + Math.random() * 100 };
            }
        } else if (spawnType === 1) {
            // Left vs Right sides
            this.team1SpawnPoint = { x: 50 + Math.random() * 100, y: 150 + Math.random() * 400 };
            this.team2SpawnPoint = { x: 850 + Math.random() * 100, y: 150 + Math.random() * 400 };
        } else {
            // Top vs Bottom sides
            this.team1SpawnPoint = { x: 200 + Math.random() * 600, y: 50 + Math.random() * 100 };
            this.team2SpawnPoint = { x: 200 + Math.random() * 600, y: 550 + Math.random() * 100 };
        }
        
        console.log(`Generated spawn points: Team1 (${Math.round(this.team1SpawnPoint.x)}, ${Math.round(this.team1SpawnPoint.y)}) vs Team2 (${Math.round(this.team2SpawnPoint.x)}, ${Math.round(this.team2SpawnPoint.y)})`);
    }

    startGame() {
        this.gameState.gameStarted = true;
        this.gameState.gameStartTime = Date.now();
        
        // Spawn initial ships for each team using generated spawn points
        const spawnPoints = {
            team1: this.team1SpawnPoint,
            team2: this.team2SpawnPoint
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
        
        // Calculate ship number - find the lowest available number (1-5)
        const ownerShips = this.gameState.ships.filter(s => s.ownerId === ownerId);
        const usedNumbers = new Set(ownerShips.map(s => s.shipNumber));
        let shipNumber = 1;
        while (usedNumbers.has(shipNumber) && shipNumber <= 5) {
            shipNumber++;
        }
        // Cap at 5 ships max per player
        if (shipNumber > 5) shipNumber = 5;
        
        const ship = {
            id: `ship_${this.gameState.nextShipId++}`,
            ownerId: ownerId,
            team: team,
            shipNumber: shipNumber,
            x: spawnPoint.x + (Math.random() - 0.5) * 60,
            y: spawnPoint.y + (Math.random() - 0.5) * 60,
            angle: angle,
            rudderAngle: 0,
            targetRudderAngle: 0,
            cannonAngle: angle,
            speed: 25,
            targetSpeed: 25,
            health: 3,
            maxHealth: 3,
            lastShot: Date.now(),
            shotCooldown: 5000,
            spawnTime: Date.now(),
            upgrades: { health: 0, damage: 0, rateOfFire: 0, speed: 0 },
            killTierProgress: 0,
            tier: 1
        };
        
        this.gameState.ships.push(ship);
        return ship;
    }

    calculateShipTier(ship) {
        if (!ship.upgrades) return 1;
        const totalUpgrades = ship.upgrades.health + ship.upgrades.damage + 
                            ship.upgrades.rateOfFire + ship.upgrades.speed;
        // Include kill progress in tier calculation
        const killProgress = (ship.killTierProgress || 0);
        const totalProgress = totalUpgrades + killProgress;
        return Math.min(Math.floor(totalProgress / 2) + 1, 5); // Max tier 5
    }

    awardKillTierProgression(killerShipId, killedShip) {
        // Find the killer ship
        const killerShip = this.gameState.ships.find(s => s.id === killerShipId);
        if (!killerShip) return;
        
        // Initialize kill progress if it doesn't exist
        if (!killerShip.killTierProgress) {
            killerShip.killTierProgress = 0;
        }
        
        // Award 0.5 tier progress for each kill (2 kills = 1 tier level)
        killerShip.killTierProgress += 0.5;
        
        // Update ship tier
        killerShip.tier = this.calculateShipTier(killerShip);
        
        console.log(`Ship ${killerShip.id} got a kill! Kill progress: ${killerShip.killTierProgress}, New tier: ${killerShip.tier}`);
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
            
            // Update speed
            if (ship.targetSpeed !== undefined) {
                const speedDiff = ship.targetSpeed - ship.speed;
                ship.speed += Math.sign(speedDiff) * Math.min(Math.abs(speedDiff), 10 * deltaTime);
            }
            
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
            id: `cannonball_${this.gameState.nextCannonballId++}`,
            shooterId: ship.id,
            shooterTeam: ship.team,
            x: ship.x + Math.cos(ship.cannonAngle) * 25,
            y: ship.y + Math.sin(ship.cannonAngle) * 25,
            angle: ship.cannonAngle,
            speed: 80,
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
                
                if (distance < 12) {
                    cannonball.dead = true;
                    ship.health -= 1;
                    
                    if (ship.health <= 0) {
                        this.gameState.scores[cannonball.shooterTeam]++;
                        
                        // Award tier progression to the killer ship
                        this.awardKillTierProgression(cannonball.shooterId, ship);
                        
                        // Respawn ship after delay
                        const team = ship.team;
                        const ownerId = ship.ownerId;
                        const spawnPoint = team === 'team1' ? this.team1SpawnPoint : this.team2SpawnPoint;
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
            players: Array.from(this.players.values()),
            spawnPoints: {
                team1: this.team1SpawnPoint,
                team2: this.team2SpawnPoint
            }
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
        const playerInfo = gameRoom.addPlayer(socket.id);
        
        socket.emit('joined-room', {
            roomId: roomId,
            playerId: socket.id,
            team: playerInfo.team,
            isHost: playerInfo.isHost,
            gameState: gameRoom.getState(),
            playerCount: gameRoom.players.size,
            playersReady: gameRoom.areAllPlayersReady()
        });
        
        socket.to(roomId).emit('player-joined', {
            playerId: socket.id,
            playerCount: gameRoom.players.size,
            playersReady: gameRoom.areAllPlayersReady()
        });
        
        console.log(`Player ${socket.id} joined room ${roomId} as ${playerInfo.team}`);
    });
    
    socket.on('start-game', (roomId) => {
        console.log(`Start game requested for room ${roomId} by ${socket.id}`);
        const gameRoom = gameRooms.get(roomId);
        const player = gameRoom?.players.get(socket.id);
        
        console.log('Game room exists:', !!gameRoom);
        console.log('Game already started:', gameRoom?.gameState.gameStarted);
        console.log('Player is host:', player?.isHost);
        console.log('Player count:', gameRoom?.players.size);
        
        // Simplified condition: host can start if game not started and enough players
        if (gameRoom && !gameRoom.gameState.gameStarted && player?.isHost && gameRoom.players.size >= 2) {
            console.log('✅ Starting game!');
            gameRoom.startGame();
            io.to(roomId).emit('game-started', {
                gameStartTime: gameRoom.gameState.gameStartTime
            });
        } else {
            console.log('❌ Cannot start game - conditions not met');
        }
    });
    
    socket.on('toggle-ready', (roomId) => {
        const gameRoom = gameRooms.get(roomId);
        if (gameRoom) {
            const readyInfo = gameRoom.togglePlayerReady(socket.id);
            if (readyInfo) {
                socket.emit('player-ready-status', readyInfo);
                socket.to(roomId).emit('players-ready', {
                    playerCount: readyInfo.playerCount,
                    playersReady: readyInfo.allPlayersReady
                });
            }
        }
    });
    
    socket.on('leave-room', () => {
        // Handle leaving room gracefully
        for (const [roomId, gameRoom] of gameRooms) {
            if (gameRoom.players.has(socket.id)) {
                socket.leave(roomId);
                gameRoom.removePlayer(socket.id);
                
                socket.to(roomId).emit('player-left', {
                    playerId: socket.id,
                    playerCount: gameRoom.players.size,
                    playersReady: gameRoom.areAllPlayersReady()
                });
                
                if (gameRoom.players.size === 0) {
                    gameRooms.delete(roomId);
                }
                break;
            }
        }
    });
    
    socket.on('ship-control', (data) => {
        // Find the room for this socket
        for (const [roomId, gameRoom] of gameRooms) {
            if (gameRoom.players.has(socket.id)) {
                const control = {};
                if (data.action === 'rudder') {
                    control.targetRudderAngle = data.value;
                } else if (data.action === 'cannon') {
                    control.cannonAngle = data.value;
                } else if (data.action === 'rudder-adjust') {
                    const ship = gameRoom.gameState.ships.find(s => s.id === data.shipId && s.ownerId === socket.id);
                    if (ship) {
                        control.targetRudderAngle = Math.max(-Math.PI/4, Math.min(Math.PI/4, ship.targetRudderAngle + data.value));
                    }
                } else if (data.action === 'speed-adjust') {
                    const ship = gameRoom.gameState.ships.find(s => s.id === data.shipId && s.ownerId === socket.id);
                    if (ship) {
                        ship.targetSpeed = Math.max(0, Math.min(50, ship.targetSpeed + data.value));
                    }
                }
                
                if (Object.keys(control).length > 0) {
                    gameRoom.updateShipControl(socket.id, data.shipId, control);
                }
                break;
            }
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
                    playerCount: gameRoom.players.size,
                    playersReady: gameRoom.areAllPlayersReady()
                });
                
                // Clean up empty rooms
                if (gameRoom.players.size === 0) {
                    gameRooms.delete(roomId);
                }
            }
        }
    });
});

const PORT = process.env.PORT || 3003;
const HOST = process.env.HOST || '0.0.0.0'; // Accept connections from any IP

server.listen(PORT, HOST, () => {
    console.log(`Game server running on http://${HOST}:${PORT}`);
    console.log(`Local access: http://localhost:${PORT}/naval_battle_server.html`);
    console.log(`Network access: http://[YOUR_IP_ADDRESS]:${PORT}/naval_battle_server.html`);
    console.log('\nTo find your IP address:');
    console.log('  Windows: ipconfig');
    console.log('  Mac/Linux: ifconfig or ip addr show');
});