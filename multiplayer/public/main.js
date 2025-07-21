// UI Elements
const menuScreen = document.getElementById('menu');
const gameScreen = document.getElementById('game');
const createRoomBtn = document.getElementById('create-room-btn');
const joinRoomBtn = document.getElementById('join-room-btn');
const roomInput = document.getElementById('room-input');
const roomCodeInput = document.getElementById('room-code');
const joinBtn = document.getElementById('join-btn');
const roomInfo = document.getElementById('room-info');
const roomCodeDisplay = document.getElementById('room-code-display');

// Game elements
const canvas = document.getElementById('gameCanvas');

// Initialize
let multiplayerManager = null;
let game = null;

// Event handlers
createRoomBtn.addEventListener('click', () => {
    multiplayerManager = new MultiplayerManager();
    
    multiplayerManager.createRoom((roomId) => {
        roomCodeDisplay.textContent = roomId;
        roomInfo.classList.remove('hidden');
        createRoomBtn.classList.add('hidden');
        joinRoomBtn.classList.add('hidden');
    });
});

joinRoomBtn.addEventListener('click', () => {
    roomInput.classList.remove('hidden');
    createRoomBtn.classList.add('hidden');
    joinRoomBtn.classList.add('hidden');
});

joinBtn.addEventListener('click', () => {
    const roomCode = roomCodeInput.value.trim();
    if (!roomCode) {
        alert('Please enter a room code');
        return;
    }

    multiplayerManager = new MultiplayerManager();
    
    multiplayerManager.joinRoom(roomCode, (success, error) => {
        if (success) {
            // Start game immediately for joiner
            menuScreen.classList.add('hidden');
            gameScreen.classList.remove('hidden');
            
            game = new Game(canvas, multiplayerManager);
            window.game = game; // Make it globally accessible
        } else {
            alert(error || 'Failed to join room');
            roomInput.classList.add('hidden');
            createRoomBtn.classList.remove('hidden');
            joinRoomBtn.classList.remove('hidden');
        }
    });
});

// Handle game start for host
document.addEventListener('DOMContentLoaded', () => {
    // Check for game start periodically when hosting
    setInterval(() => {
        if (multiplayerManager && multiplayerManager.isHost && !game && multiplayerManager.dataChannel) {
            menuScreen.classList.add('hidden');
            gameScreen.classList.remove('hidden');
            
            game = new Game(canvas, multiplayerManager);
            window.game = game;
        }
    }, 100);
});