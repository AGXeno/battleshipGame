# Naval Battle WebRTC Signaling Server

## Setup Instructions

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the server:**
   ```bash
   npm start
   ```
   Or for development with auto-restart:
   ```bash
   npm run dev
   ```

3. **Access the game:**
   Open your browser and navigate to:
   ```
   http://localhost:3001/naval_battle.html
   ```

## How it works

- The server runs on port 3001 by default (configurable via `PORT` environment variable)
- It serves static files from the project directory (including naval_battle.html)
- Handles WebRTC signaling for peer-to-peer connections between players
- Manages game rooms and player connections

## Server Features

- **Room Management**: Players can join/leave rooms
- **WebRTC Signaling**: Relays offers, answers, and ICE candidates between peers
- **Player Tracking**: Keeps track of players in each room
- **Auto-cleanup**: Removes empty rooms when all players leave

## Testing Multiplayer

1. Start the server as described above
2. Open two browser windows/tabs
3. Navigate to `http://localhost:3001/naval_battle.html` in both
4. Join the same room ID in both windows
5. The WebRTC connection will be established automatically