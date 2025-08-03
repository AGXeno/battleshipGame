# Deploy Naval Battle to Render.com (Free!)

No ngrok needed! Get a permanent URL like `https://naval-battle.onrender.com`

## Steps:

### 1. Push your code to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin webrtc-jjacobson-merge
```

### 2. Sign up at Render.com
- Go to: https://render.com
- Sign up with GitHub (free)

### 3. Create New Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repo
- Select your repository

### 4. Configure:
- **Name**: naval-battle (or whatever you want)
- **Environment**: Node
- **Root Directory**: `server`
- **Build Command**: `npm install`
- **Start Command**: `node game-server.js`
- **Plan**: Free

### 5. Deploy!
- Click "Create Web Service"
- Wait 2-3 minutes for deployment
- You'll get a URL like: `https://naval-battle.onrender.com`

### That's it! 
Share the URL with anyone - no IP addresses, no ngrok needed!

## Why Render instead of Vercel?
- Vercel = Great for static sites, but no WebSocket support
- Render = Supports WebSockets (needed for multiplayer)
- Both are free!

## Note:
Free tier on Render spins down after 15 minutes of inactivity, but spins back up when someone visits (takes ~30 seconds).