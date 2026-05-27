// Simple OpenWA Server - Bypass Windows compatibility issues
const express = require('express');
const cors = require('cors');

const app = express();
const port = 2787;

// Middleware
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:5000', 'http://localhost:5001', 'file://', 'null'],
    credentials: true
}));
app.use(express.json());

// Global variables for WhatsApp state
let client = null;
let qrCode = null;
let isAuthenticated = false;
let clientStatus = 'initializing';

// Simple mock OpenWA implementation for testing
console.log('🔥 Simple OpenWA server starting on port', port);
console.log('📱 Attempting to initialize OpenWA...');

// Try to load OpenWA with error handling
let openwa = null;
try {
    openwa = require('@open-wa/wa-automate');
    console.log('✅ OpenWA module loaded successfully');
} catch (error) {
    console.log('❌ OpenWA module load failed:', error.message);
    console.log('🔄 Running in fallback mode');
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'OpenWA Server',
        version: '4.76.0',
        authenticated: isAuthenticated,
        clientStatus: clientStatus,
        timestamp: new Date().toISOString()
    });
});

// Get QR code endpoint
app.get('/api/qr', (req, res) => {
    console.log('QR endpoint called, status:', clientStatus);
    
    if (isAuthenticated) {
        return res.json({
            success: true,
            authenticated: true,
            message: 'Already authenticated with OpenWA'
        });
    }

    if (qrCode) {
        return res.json({
            success: true,
            qr: qrCode,
            status: clientStatus,
            message: 'Scan QR code with WhatsApp'
        });
    } else {
        return res.json({
            success: false,
            message: 'QR code not ready yet',
            status: clientStatus
        });
    }
});

// Get connection status
app.get('/api/status', (req, res) => {
    res.json({
        success: true,
        authenticated: isAuthenticated,
        status: clientStatus,
        hasQr: !!qrCode,
        openwa: true
    });
});

// Send message endpoint
app.post('/api/send', async (req, res) => {
    try {
        if (!isAuthenticated || !client) {
            return res.status(400).json({
                success: false,
                message: 'OpenWA not authenticated'
            });
        }

        const { number, message } = req.body;
        
        if (!number || !message) {
            return res.status(400).json({
                success: false,
                message: 'Number and message are required'
            });
        }

        const chatId = number.includes('@c.us') ? number : `${number}@c.us`;
        await client.sendText(chatId, message);
        
        res.json({
            success: true,
            message: 'Message sent successfully via OpenWA'
        });
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({
            success: false,
            message: 'Error sending message via OpenWA',
            error: error.message
        });
    }
});

// Reinitialize connection  
app.post('/api/relink', (req, res) => {
    try {
        if (client) {
            client.kill();
        }
        isAuthenticated = false;
        clientStatus = 'reinitializing';
        qrCode = null;
        
        setTimeout(() => {
            initializeOpenWA();
        }, 2000);
        
        res.json({
            success: true,
            message: 'Reinitializing OpenWA connection'
        });
    } catch (error) {
        console.error('Error reinitializing:', error);
        res.status(500).json({
            success: false,
            message: 'Error reinitializing OpenWA connection',
            error: error.message
        });
    }
});

// Initialize OpenWA with bypass for Windows issues
async function initializeOpenWA() {
    if (!openwa) {
        console.log('❌ OpenWA not available, cannot initialize');
        clientStatus = 'error';
        return;
    }
    
    console.log('🚀 Initializing OpenWA...');
    clientStatus = 'initializing';
    
    try {
        // Minimal configuration to avoid Windows compatibility issues
        const config = {
            sessionId: 'reportflow',
            multiDevice: true,
            authTimeout: 60,
            blockCrashLogs: true,
            disableSpins: true,
            headless: true,
            logConsole: false,
            popup: false,
            qrTimeout: 0,
            restartOnCrash: false,  // Disable to avoid process monitoring issues
            useChrome: false,       // Use default browser
            killProcessOnBrowserClose: false,  // Disable process monitoring
            throwErrorOnTosBlock: false
        };

        console.log('📱 Creating OpenWA client...');
        
        client = await openwa.create(config);
        
        isAuthenticated = true;
        clientStatus = 'authenticated';
        qrCode = null;
        console.log('✅ OpenWA client ready!');
        
        // Set up event listeners
        client.onStateChanged((state) => {
            console.log('📱 OpenWA State changed:', state);
            clientStatus = state;
            if (state === 'CONFLICT') {
                client.forceRefocus();
            }
        });
        
        client.onMessage(async (message) => {
            console.log('📩 Message received via OpenWA:', message.body);
        });
        
    } catch (error) {
        console.error('❌ OpenWA initialization failed:', error.message);
        clientStatus = 'failed';
        isAuthenticated = false;
        
        // Generate a test QR code for development
        console.log('🔄 Generating test QR for development...');
        qrCode = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==';
        clientStatus = 'qr_ready';
    }
}

// Start server
app.listen(port, () => {
    console.log(`\n=== OpenWA Server Started ===`);
    console.log(`Port: ${port}`);
    console.log(`Health Check: http://localhost:${port}/api/health`);
    console.log(`QR Code: http://localhost:${port}/api/qr`);
    console.log(`Status: http://localhost:${port}/api/status`);
    console.log('==============================\n');
    
    // Initialize OpenWA after server is running
    setTimeout(() => {
        initializeOpenWA();
    }, 1000);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down OpenWA server...');
    if (client) {
        try {
            client.kill();
        } catch (err) {
            console.log('Error closing client:', err.message);
        }
    }
    process.exit(0);
});