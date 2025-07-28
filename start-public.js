const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting Naval Battle Game with Public Access...\n');

// Start the game server
console.log('1️⃣ Starting game server...');
const server = spawn('node', ['game-server.js'], {
    stdio: 'pipe',
    cwd: __dirname
});

server.stdout.on('data', (data) => {
    console.log(`[SERVER] ${data.toString().trim()}`);
});

server.stderr.on('data', (data) => {
    console.error(`[SERVER ERROR] ${data.toString().trim()}`);
});

// Wait a moment for server to start, then start tunnel
setTimeout(() => {
    console.log('\n2️⃣ Creating public tunnel...');
    const tunnel = spawn('lt', ['--port', '3002'], {
        stdio: 'pipe'
    });

    tunnel.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output.includes('your url is:')) {
            const url = output.split('your url is: ')[1];
            console.log('\n🌐 PUBLIC URL READY!');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`🎮 Game URL: ${url}/naval_battle_server.html`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log('\n📋 Instructions:');
            console.log('1. Copy the Game URL above');
            console.log('2. Share it with friends');
            console.log('3. Everyone opens the URL and joins the same room');
            console.log('4. Start playing!');
            console.log('\n⚠️  Keep this terminal open to maintain the connection');
            console.log('📝 Press Ctrl+C to stop the server and tunnel');
        } else {
            console.log(`[TUNNEL] ${output}`);
        }
    });

    tunnel.stderr.on('data', (data) => {
        console.error(`[TUNNEL ERROR] ${data.toString().trim()}`);
    });

    tunnel.on('close', (code) => {
        console.log('\n❌ Tunnel closed');
        server.kill();
        process.exit(0);
    });

}, 2000);

server.on('close', (code) => {
    console.log('\n❌ Server stopped');
    process.exit(0);
});

// Handle Ctrl+C
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down...');
    server.kill();
    process.exit(0);
});