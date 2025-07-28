const os = require('os');

function getLocalIPAddress() {
    const interfaces = os.networkInterfaces();
    
    console.log('🌐 Naval Battle Game - Network Information\n');
    console.log('Available network interfaces:');
    
    for (const [name, addresses] of Object.entries(interfaces)) {
        const ipv4 = addresses.find(addr => addr.family === 'IPv4' && !addr.internal);
        if (ipv4) {
            console.log(`  ${name}: ${ipv4.address}`);
            
            // Likely the main WiFi/Ethernet connection
            if (name.toLowerCase().includes('wi-fi') || 
                name.toLowerCase().includes('wifi') || 
                name.toLowerCase().includes('wlan') ||
                name.toLowerCase().includes('ethernet') ||
                name.toLowerCase().includes('eth')) {
                console.log(`    👆 This is likely your main connection`);
            }
        }
    }
    
    console.log('\n📋 Instructions:');
    console.log('1. Start the game server: npm start');
    console.log('2. Share this URL with others on your network:');
    
    const mainIP = getMainIPAddress();
    if (mainIP) {
        console.log(`   http://${mainIP}:3001/naval_battle_server.html`);
        console.log('\n🎮 Have everyone open this URL and join the same room!');
    } else {
        console.log('   http://[YOUR_IP_ADDRESS]:3001/naval_battle_server.html');
        console.log('   (Replace [YOUR_IP_ADDRESS] with one of the IPs above)');
    }
    
    console.log('\n🔥 For internet access, check DEPLOYMENT.md for cloud hosting options');
}

function getMainIPAddress() {
    const interfaces = os.networkInterfaces();
    
    // Priority order for interface names
    const priorities = ['wi-fi', 'wifi', 'wlan', 'ethernet', 'eth0', 'en0'];
    
    for (const priority of priorities) {
        for (const [name, addresses] of Object.entries(interfaces)) {
            if (name.toLowerCase().includes(priority)) {
                const ipv4 = addresses.find(addr => addr.family === 'IPv4' && !addr.internal);
                if (ipv4) {
                    return ipv4.address;
                }
            }
        }
    }
    
    // Fallback: return first non-internal IPv4
    for (const addresses of Object.values(interfaces)) {
        const ipv4 = addresses.find(addr => addr.family === 'IPv4' && !addr.internal);
        if (ipv4) {
            return ipv4.address;
        }
    }
    
    return null;
}

getLocalIPAddress();