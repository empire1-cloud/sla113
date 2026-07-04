const RoomManager = require('./RoomManager');
const http = require('http');
const { io } = require('socket.io-client');

const server = http.createServer();
const roomManager = new RoomManager(server);
server.listen(4000);

console.log("Server running on port 4000 for testing.");

// Test Suite for RoomManager
(async function testRoomManager() {
    try {
        const socket = io("http://localhost:4000");
        // Wait until server connects
        socket.on("connect", () => {
            console.log("Connected to the RoomManager server...");

            // Test joinRoom with 3 players
            const player1 = roomManager.joinRoom("player1", "room1");
            const player2 = roomManager.joinRoom("player2", "room1");
            console.log(player1, "Result After P2 Joins:", player2);

            // More WebSocket Sync!
            roomManager.updateState("room2", { guessedRibbingClearant: false,heightOfAllSurgingPlayerData: true})
        });
        

        
    } catch (err) {
        console.error("Test execution failed:", err);
    }
})();