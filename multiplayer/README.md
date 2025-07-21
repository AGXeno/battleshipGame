# Sea Ping Warfare - Multiplayer Mode

Browser-based multiplayer version of Sea Ping Warfare using WebRTC for peer-to-peer gameplay.

## Quick Start

### 1. Install Dependencies
```bash
cd multiplayer
npm install
```

### 2. Start the Server

**For Internet Play (Recommended):**
```bash
use-serveo.bat
```
This creates a public URL (like `https://something.serveo.net`) that both players can access from anywhere.

**For Local Network Play:**
```bash
npm start
```
- Player 1: Open `http://localhost:3000`
- Player 2: Open `http://<player1-computer-ip>:3000`

## How to Play

1. **Host creates a room:**
   - Click "Create Room"
   - Share the room code with opponent

2. **Opponent joins:**
   - Click "Join Room"
   - Enter the room code
   - Click "Join"

3. **Game starts automatically when both players connect**

## Controls

- **WASD** - Move your ship
- **Arrow Keys** - Rotate turret
- **Space** - Fire cannonball

## Game Rules

- Each player has 3 health points
- Cannonballs bounce off walls (max 2 bounces)
- First player to destroy the opponent wins
- If a player disconnects, the game ends

## Technical Details

- WebRTC peer-to-peer connection
- 60 FPS synchronized gameplay
- Low latency direct connection between players
- Socket.io used only for initial connection setup