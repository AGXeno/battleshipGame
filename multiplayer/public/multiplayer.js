class MultiplayerManager {
    constructor() {
        this.socket = io();
        this.peerConnection = null;
        this.dataChannel = null;
        this.roomId = null;
        this.isHost = false;
        this.localPlayerId = null;
        this.remotePlayerId = null;
        this.onGameStart = null;
        this.onGameStateReceived = null;
        
        this.setupSocketListeners();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to signaling server');
            this.localPlayerId = this.socket.id;
        });

        this.socket.on('player-joined', async (data) => {
            console.log('Player joined:', data.playerId);
            this.remotePlayerId = data.playerId;
            if (this.isHost) {
                await this.createOffer();
            }
        });

        this.socket.on('offer', async (data) => {
            console.log('Received offer from:', data.from);
            this.remotePlayerId = data.from;
            await this.handleOffer(data.offer);
        });

        this.socket.on('answer', async (data) => {
            console.log('Received answer from:', data.from);
            await this.handleAnswer(data.answer);
        });

        this.socket.on('ice-candidate', async (data) => {
            console.log('Received ICE candidate from:', data.from);
            await this.handleIceCandidate(data.candidate);
        });

        this.socket.on('player-disconnected', (data) => {
            console.log('Player disconnected:', data.playerId);
            this.handlePlayerDisconnect();
        });
    }

    createRoom(callback) {
        this.socket.emit('create-room', (response) => {
            if (response.roomId) {
                this.roomId = response.roomId;
                this.isHost = true;
                callback(response.roomId);
            }
        });
    }

    joinRoom(roomId, callback) {
        this.socket.emit('join-room', roomId, async (response) => {
            if (response.success) {
                this.roomId = roomId;
                this.isHost = false;
                callback(true);
                
                // If there's already another player, we'll receive an offer
                if (response.players.length === 2) {
                    console.log('Room is full, waiting for offer...');
                }
            } else {
                callback(false, response.error);
            }
        });
    }

    async setupPeerConnection() {
        const configuration = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };

        this.peerConnection = new RTCPeerConnection(configuration);

        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.socket.emit('ice-candidate', {
                    to: this.remotePlayerId,
                    candidate: event.candidate
                });
            }
        };

        this.peerConnection.ondatachannel = (event) => {
            const channel = event.channel;
            this.setupDataChannel(channel);
        };
    }

    setupDataChannel(channel) {
        this.dataChannel = channel;
        
        this.dataChannel.onopen = () => {
            console.log('Data channel opened');
            if (this.onGameStart) {
                this.onGameStart();
            }
        };

        this.dataChannel.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (this.onGameStateReceived) {
                this.onGameStateReceived(data);
            }
        };

        this.dataChannel.onerror = (error) => {
            console.error('Data channel error:', error);
        };

        this.dataChannel.onclose = () => {
            console.log('Data channel closed');
            this.handlePlayerDisconnect();
        };
    }

    async createOffer() {
        await this.setupPeerConnection();
        
        // Create data channel
        const channel = this.peerConnection.createDataChannel('gameData', {
            ordered: true
        });
        this.setupDataChannel(channel);

        const offer = await this.peerConnection.createOffer();
        await this.peerConnection.setLocalDescription(offer);

        this.socket.emit('offer', {
            to: this.remotePlayerId,
            offer: offer
        });
    }

    async handleOffer(offer) {
        await this.setupPeerConnection();
        
        await this.peerConnection.setRemoteDescription(offer);
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);

        this.socket.emit('answer', {
            to: this.remotePlayerId,
            answer: answer
        });
    }

    async handleAnswer(answer) {
        await this.peerConnection.setRemoteDescription(answer);
    }

    async handleIceCandidate(candidate) {
        if (this.peerConnection) {
            await this.peerConnection.addIceCandidate(candidate);
        }
    }

    sendGameState(state) {
        if (this.dataChannel && this.dataChannel.readyState === 'open') {
            this.dataChannel.send(JSON.stringify(state));
        }
    }

    handlePlayerDisconnect() {
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        this.dataChannel = null;
        
        // Notify game to handle disconnect
        if (window.game) {
            window.game.handleOpponentDisconnect();
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
        if (this.peerConnection) {
            this.peerConnection.close();
        }
    }
}