# Naval Battle Game Server

## Setup Instructions

1. **Install dependencies:**
   ```bash
   cd server
   npm install
   ```

2. **Start the server:**
   ```bash
   cd server
   node game-server.js
   ```

3. **Access the game:**
   Open your browser and navigate to:
   ```
   http://localhost:3003
   ```

## How it works

- The server runs on port 3003 by default (configurable via `PORT` environment variable)
- It serves static files from the root project directory
- Handles real-time multiplayer game state via Socket.io
- Manages game rooms and player connections

## Server Features

- **Room Management**: Players can join/leave rooms
- **Real-time Game State**: Synchronizes ship positions, combat, and scores
- **Player Tracking**: Keeps track of players in each room
- **Auto-cleanup**: Removes empty rooms when all players leave

## Game Modes

1. **Single Player**: Play against AI (no server needed - open naval_battle_single.html directly)
2. **Multiplayer**: Real-time PvP via server
3. **Demo**: AI vs AI demonstration (no server needed - open naval_battle_demo.html directly)

## Testing Multiplayer

1. Start the server as described above
2. Open browser and go to `http://localhost:3003`
3. Click "Multiplayer" → Enter room name → "Join Room"
4. Have another player do the same with the same room name
5. Host clicks "Start Game" when both players are ready 

:)