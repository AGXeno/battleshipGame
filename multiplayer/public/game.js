class Player {
    constructor(x, y, isLocal) {
        this.x = x;
        this.y = y;
        this.width = 40;
        this.height = 30;
        this.turretAngle = 0;
        this.health = 3;
        this.isLocal = isLocal;
        this.cooldown = 0;
        this.hitFlash = 0;
        this.speed = 3;
    }

    update(input) {
        if (this.isLocal && input) {
            // Movement
            if (input.left) this.x -= this.speed;
            if (input.right) this.x += this.speed;
            if (input.up) this.y -= this.speed;
            if (input.down) this.y += this.speed;

            // Turret rotation
            if (input.rotateLeft) this.turretAngle -= 0.05;
            if (input.rotateRight) this.turretAngle += 0.05;
        }

        // Update cooldown
        if (this.cooldown > 0) this.cooldown--;
        if (this.hitFlash > 0) this.hitFlash--;
    }

    canShoot() {
        return this.cooldown === 0;
    }

    shoot() {
        if (this.canShoot()) {
            this.cooldown = 30; // 0.5 seconds at 60 FPS
            return new Cannonball(
                this.x + this.width / 2,
                this.y + this.height / 2,
                this.turretAngle,
                this.isLocal ? 'local' : 'remote'
            );
        }
        return null;
    }

    takeDamage() {
        this.health--;
        this.hitFlash = 10;
    }

    draw(ctx) {
        ctx.save();

        // Draw body
        ctx.fillStyle = this.hitFlash > 0 ? '#ff6666' : (this.isLocal ? '#4169e1' : '#dc143c');
        ctx.fillRect(this.x, this.y, this.width, this.height);

        // Draw turret
        ctx.translate(this.x + this.width / 2, this.y + this.height / 2);
        ctx.rotate(this.turretAngle);
        ctx.fillStyle = '#333';
        ctx.fillRect(-3, -20, 6, 20);
        
        ctx.restore();
    }

    getState() {
        return {
            x: this.x,
            y: this.y,
            turretAngle: this.turretAngle,
            health: this.health,
            cooldown: this.cooldown
        };
    }

    setState(state) {
        this.x = state.x;
        this.y = state.y;
        this.turretAngle = state.turretAngle;
        this.health = state.health;
        this.cooldown = state.cooldown;
    }
}

class Cannonball {
    constructor(x, y, angle, owner) {
        this.x = x;
        this.y = y;
        this.radius = 5;
        this.speed = 8;
        this.vx = Math.sin(angle) * this.speed;
        this.vy = -Math.cos(angle) * this.speed;
        this.owner = owner;
        this.bounces = 0;
        this.maxBounces = 2;
        this.lifetime = 300; // 5 seconds at 60 FPS
        this.active = true;
    }

    update(canvas) {
        this.x += this.vx;
        this.y += this.vy;
        this.lifetime--;

        // Wall bouncing
        if (this.x - this.radius <= 0 || this.x + this.radius >= canvas.width) {
            this.vx = -this.vx;
            this.bounces++;
        }
        if (this.y - this.radius <= 0 || this.y + this.radius >= canvas.height) {
            this.vy = -this.vy;
            this.bounces++;
        }

        // Deactivate if exceeded bounces or lifetime
        if (this.bounces > this.maxBounces || this.lifetime <= 0) {
            this.active = false;
        }
    }

    draw(ctx) {
        ctx.fillStyle = this.owner === 'local' ? '#00f' : '#f00';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
    }

    checkCollision(player) {
        const dx = this.x - (player.x + player.width / 2);
        const dy = this.y - (player.y + player.height / 2);
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < this.radius + Math.max(player.width, player.height) / 2;
    }

    getState() {
        return {
            x: this.x,
            y: this.y,
            vx: this.vx,
            vy: this.vy,
            owner: this.owner,
            bounces: this.bounces,
            lifetime: this.lifetime,
            active: this.active
        };
    }

    static fromState(state) {
        const ball = new Cannonball(0, 0, 0, state.owner);
        ball.x = state.x;
        ball.y = state.y;
        ball.vx = state.vx;
        ball.vy = state.vy;
        ball.bounces = state.bounces;
        ball.lifetime = state.lifetime;
        ball.active = state.active;
        return ball;
    }
}

class Game {
    constructor(canvas, multiplayerManager) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.multiplayer = multiplayerManager;
        
        // Set canvas size
        this.canvas.width = 800;
        this.canvas.height = 600;
        
        // Game state
        this.localPlayer = null;
        this.remotePlayer = null;
        this.cannonballs = [];
        this.gameActive = false;
        this.winner = null;
        
        // Input handling
        this.input = {
            left: false,
            right: false,
            up: false,
            down: false,
            rotateLeft: false,
            rotateRight: false,
            shoot: false
        };
        
        this.setupInput();
        this.setupMultiplayer();
    }

    setupInput() {
        document.addEventListener('keydown', (e) => {
            switch(e.key.toLowerCase()) {
                case 'a': this.input.left = true; break;
                case 'd': this.input.right = true; break;
                case 'w': this.input.up = true; break;
                case 's': this.input.down = true; break;
                case 'arrowleft': this.input.rotateLeft = true; break;
                case 'arrowright': this.input.rotateRight = true; break;
                case ' ': this.input.shoot = true; break;
            }
        });

        document.addEventListener('keyup', (e) => {
            switch(e.key.toLowerCase()) {
                case 'a': this.input.left = false; break;
                case 'd': this.input.right = false; break;
                case 'w': this.input.up = false; break;
                case 's': this.input.down = false; break;
                case 'arrowleft': this.input.rotateLeft = false; break;
                case 'arrowright': this.input.rotateRight = false; break;
                case ' ': this.input.shoot = false; break;
            }
        });
    }

    setupMultiplayer() {
        this.multiplayer.onGameStart = () => {
            this.startGame();
        };

        this.multiplayer.onGameStateReceived = (state) => {
            this.applyRemoteState(state);
        };
    }

    startGame() {
        // Initialize players
        if (this.multiplayer.isHost) {
            this.localPlayer = new Player(100, 300, true);
            this.remotePlayer = new Player(700, 300, false);
        } else {
            this.localPlayer = new Player(700, 300, true);
            this.remotePlayer = new Player(100, 300, false);
        }
        
        this.gameActive = true;
        this.gameLoop();
    }

    update() {
        if (!this.gameActive) return;

        // Update local player
        this.localPlayer.update(this.input);

        // Handle shooting
        if (this.input.shoot) {
            const cannonball = this.localPlayer.shoot();
            if (cannonball) {
                this.cannonballs.push(cannonball);
            }
        }

        // Update cannonballs
        this.cannonballs = this.cannonballs.filter(ball => {
            ball.update(this.canvas);
            
            // Check collisions
            if (ball.active && ball.owner === 'remote' && ball.checkCollision(this.localPlayer)) {
                this.localPlayer.takeDamage();
                ball.active = false;
            }
            if (ball.active && ball.owner === 'local' && ball.checkCollision(this.remotePlayer)) {
                this.remotePlayer.takeDamage();
                ball.active = false;
            }
            
            return ball.active;
        });

        // Check win conditions
        if (this.localPlayer.health <= 0) {
            this.gameActive = false;
            this.winner = 'Player 2';
        } else if (this.remotePlayer.health <= 0) {
            this.gameActive = false;
            this.winner = 'Player 1';
        }

        // Send state to remote player
        this.sendGameState();
    }

    sendGameState() {
        const state = {
            player: this.localPlayer.getState(),
            cannonballs: this.cannonballs
                .filter(ball => ball.owner === 'local')
                .map(ball => ball.getState()),
            timestamp: Date.now()
        };
        this.multiplayer.sendGameState(state);
    }

    applyRemoteState(state) {
        // Update remote player
        if (state.player) {
            this.remotePlayer.setState(state.player);
        }

        // Update remote cannonballs
        if (state.cannonballs) {
            // Remove old remote cannonballs
            this.cannonballs = this.cannonballs.filter(ball => ball.owner !== 'remote');
            
            // Add new remote cannonballs
            state.cannonballs.forEach(ballState => {
                const ball = Cannonball.fromState(ballState);
                ball.owner = 'remote'; // Ensure it's marked as remote
                this.cannonballs.push(ball);
            });
        }
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#87CEEB';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw water effect
        this.ctx.fillStyle = '#4682B4';
        for (let i = 0; i < this.canvas.width; i += 40) {
            this.ctx.fillRect(i, this.canvas.height - 50, 30, 50);
        }

        // Draw players
        if (this.localPlayer) this.localPlayer.draw(this.ctx);
        if (this.remotePlayer) this.remotePlayer.draw(this.ctx);

        // Draw cannonballs
        this.cannonballs.forEach(ball => ball.draw(this.ctx));

        // Update UI
        this.updateUI();

        // Draw game over
        if (!this.gameActive && this.winner) {
            const status = document.getElementById('game-status');
            status.textContent = `${this.winner} Wins!`;
            status.style.display = 'block';
        }
    }

    updateUI() {
        if (this.localPlayer && this.remotePlayer) {
            document.getElementById('p1-health').textContent = 
                this.multiplayer.isHost ? this.localPlayer.health : this.remotePlayer.health;
            document.getElementById('p2-health').textContent = 
                this.multiplayer.isHost ? this.remotePlayer.health : this.localPlayer.health;
        }
    }

    gameLoop() {
        this.update();
        this.draw();

        if (this.gameActive) {
            requestAnimationFrame(() => this.gameLoop());
        }
    }

    handleOpponentDisconnect() {
        this.gameActive = false;
        const status = document.getElementById('game-status');
        status.textContent = 'Opponent Disconnected';
        status.style.display = 'block';
    }
}