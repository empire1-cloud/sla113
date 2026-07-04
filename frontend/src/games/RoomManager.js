const { Server } = require("socket.io");

class RoomManager {
    constructor(server) {
        this.io = new Server(server); // Bind the WebSocket server
        this.rooms = {}; // Track rooms and players within them
    }

    /**
     * joinRoom: Create or join a room with SceneID enforcement
     * @param {string} playerId
     * @param {string} roomId
     * @param {string} sceneId
     */
    joinRoom(playerId, roomId, sceneId) {
        // Initialize room if it doesn't exist
        if (!this.rooms[roomId]) {
            this.rooms[roomId] = {
                players: [],
                assets: [],
                maxSeats: 4,
                sceneId: null,
                state: {}
            };
        }

        const room = this.rooms[roomId];

        // Scene Mismatch Check
        if (room.sceneId && room.sceneId !== sceneId) {
            return { 
                success: false, 
                message: "Scene mismatch. Cannot join room with different assets." 
            };
        }

        // Lock scene if not set
        if (!room.sceneId) {
            room.sceneId = sceneId;
        }

        // Check availability
        if (room.players.length >= room.maxSeats) {
            return { success: false, message: "Room is full" };
        }

        // Add player
        if (!room.players.includes(playerId)) {
            room.players.push(playerId);
        }

        // Broadcast update
        this.io.to(roomId).emit("room_update", this.getRoomState(roomId));

        return { success: true, message: "Joined room", room };
    }

    /**
     * updateState: Sync game state and handle asset collision
     * @param {string} roomId
     * @param {object} updateData
     */
    updateState(roomId, updateData) {
        if (!this.rooms[roomId]) {
            return { success: false, message: "Room not found" };
        }

        const { gameAssets, ...state } = updateData;

        // Prevent zero-overlap assets by SceneID
        if (gameAssets && Array.isArray(gameAssets)) {
            const hasOverlap = this.rooms[roomId].assets.some(asset => gameAssets.includes(asset));
            if (hasOverlap) {
                return { success: false, message: "Asset overlap detected. Cannot update state." };
            }
            this.rooms[roomId].assets = gameAssets;
        }

        // Update and Merge State
        this.rooms[roomId].state = { ...this.rooms[roomId].state, ...state };
        
        // Emit to all connected players
        this.io.to(roomId).emit("state_update", this.rooms[roomId].state);
        
        return { success: true };
    }

    /**
     * getRoomState: Utility to fetch current room data
     * @param {string} roomId
     */
    getRoomState(roomId) {
        const room = this.rooms[roomId];
        return room ? { players: room.players, state: room.state || {} } : null;
    }
}

module.exports = RoomManager;