# Naval Battle Game - Deployment Guide

## Options for Multiplayer Hosting

### Option 1: Local Network (Same WiFi)
**Best for:** Testing with friends on the same WiFi network

1. Start the server:
   ```bash
   npm start
   ```

2. Find your computer's IP address:
   - **Windows:** Open Command Prompt, run `ipconfig`, look for "IPv4 Address"
   - **Mac:** Open Terminal, run `ifconfig`, look for your WiFi adapter's inet address
   - **Linux:** Run `ip addr show` or `ifconfig`

3. Share the URL with others:
   - Replace `[YOUR_IP_ADDRESS]` with your actual IP
   - Example: `http://192.168.1.100:3001/naval_battle_server.html`

4. Make sure your firewall allows connections on port 3001

### Option 2: Cloud Hosting (Internet Access)
**Best for:** Playing with anyone online

#### Deploy to Render (Free)
1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Create a new "Web Service"
4. Connect your GitHub repository
5. Use these settings:
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
   - **Environment:** Node
6. Deploy and get your public URL

#### Deploy to Heroku (Free tier discontinued, but still available)
1. Install Heroku CLI
2. Run these commands:
   ```bash
   heroku create your-naval-battle-game
   git add .
   git commit -m "Deploy naval battle game"
   git push heroku main
   ```

#### Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-deploy

### Option 3: Tunneling Services (Quick Testing)
**Best for:** Quick testing without cloud deployment

#### Ngrok (requires account)
1. Install ngrok: [ngrok.com/download](https://ngrok.com/download)
2. Create free account and get auth token
3. Start your server: `npm start`
4. In another terminal: `ngrok http 3001`
5. Use the provided public URL

#### LocalTunnel (no account needed)
1. Install: `npm install -g localtunnel`
2. Start your server: `npm start`
3. In another terminal: `lt --port 3001`
4. Use the provided URL (e.g., `https://gentle-penguin-42.loca.lt/naval_battle_server.html`)

#### Serveo (no install needed)
1. Start your server: `npm start`
2. Run: `ssh -R 80:localhost:3001 serveo.net`
3. Use the provided URL

#### Localhost.run (no install needed)
1. Start your server: `npm start`
2. Run: `ssh -R 80:localhost:3001 ssh.localhost.run`
3. Use the provided URL

### Option 4: Port Forwarding (Advanced)
**Best for:** Permanent home server setup

1. Access your router's admin panel (usually `192.168.1.1`)
2. Find "Port Forwarding" settings
3. Forward external port 3001 to your computer's IP:3001
4. Use your public IP address (find at [whatismyip.com](https://whatismyip.com))

## Environment Variables

Create a `.env` file for different configurations:

```bash
# .env
PORT=3001
HOST=0.0.0.0
NODE_ENV=production
```

## Security Notes

- The current setup is for development/testing
- For production, consider adding:
  - Rate limiting
  - Authentication
  - HTTPS/SSL certificates
  - Input validation
  - Anti-cheat measures

## Testing Your Deployment

1. Start the server
2. Open the game URL in your browser
3. Have someone else open the same URL
4. Both join the same room ID
5. Start playing!

## Troubleshooting

**Can't connect from other devices:**
- Check firewall settings
- Ensure you're using the correct IP address
- Make sure both devices are on the same network (for local hosting)

**Server crashes:**
- Check the console for error messages
- Ensure all dependencies are installed: `npm install`
- Try restarting: `npm start`

**Game feels laggy:**
- For cloud hosting, choose a server region close to players
- For local hosting, ensure good WiFi connection
- Consider reducing the update rate in the server code