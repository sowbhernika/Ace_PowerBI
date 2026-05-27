const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const express = require('express');
const QRCode = require('qrcode');
const cors = require('cors');

const app = express();
app.use(cors({
    origin: ['http://localhost:5001', 'file://', 'null'],
    credentials: true
}));
app.use(express.json({ limit: '50mb' }));

let client = null;
let qrCodeString = '';
let isAuthenticated = false;
let clientStatus = 'initializing';

function initializeWhatsApp() {
    console.log('Initializing WhatsApp client...');
    
    client = new Client({
        authStrategy: new LocalAuth({
            clientId: "reportflow"
        }),
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
        }
    });

    client.on('qr', (qr) => {
        console.log('QR Code received');
        qrCodeString = qr;
        clientStatus = 'qr_ready';
        
        QRCode.toDataURL(qr, (err, url) => {
            if (err) {
                console.error('Error generating QR code:', err);
            } else {
                console.log('QR Code generated successfully');
            }
        });
    });

    client.on('ready', () => {
        console.log('WhatsApp client is ready!');
        isAuthenticated = true;
        clientStatus = 'authenticated';
        qrCodeString = '';
    });

    client.on('authenticated', () => {
        console.log('WhatsApp client authenticated');
        isAuthenticated = true;
        clientStatus = 'authenticated';
    });

    client.on('auth_failure', () => {
        console.log('Authentication failed');
        isAuthenticated = false;
        clientStatus = 'auth_failed';
    });

    client.on('disconnected', (reason) => {
        console.log('WhatsApp client disconnected:', reason);
        isAuthenticated = false;
        clientStatus = 'disconnected';
        qrCodeString = '';
    });

    client.initialize();
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Get QR code for authentication
app.get('/api/qr', async (req, res) => {
    try {
        if (isAuthenticated) {
            return res.json({ 
                success: true, 
                authenticated: true, 
                message: 'Already authenticated' 
            });
        }

        if (qrCodeString) {
            const qrDataURL = await QRCode.toDataURL(qrCodeString);
            return res.json({
                success: true,
                qr: qrDataURL,
                qr_text: qrCodeString,
                status: clientStatus
            });
        } else {
            return res.json({
                success: false,
                message: 'QR code not ready yet',
                status: clientStatus
            });
        }
    } catch (error) {
        console.error('Error generating QR:', error);
        res.status(500).json({
            success: false,
            message: 'Error generating QR code',
            error: error.message
        });
    }
});

// Get connection status
app.get('/api/status', (req, res) => {
    res.json({
        success: true,
        authenticated: isAuthenticated,
        status: clientStatus,
        has_qr: !!qrCodeString
    });
});

// Reinitialize connection
app.post('/api/relink', (req, res) => {
    try {
        if (client) {
            client.destroy();
        }
        isAuthenticated = false;
        clientStatus = 'reinitializing';
        qrCodeString = '';
        
        setTimeout(() => {
            initializeWhatsApp();
        }, 2000);
        
        res.json({
            success: true,
            message: 'Reinitializing WhatsApp connection'
        });
    } catch (error) {
        console.error('Error reinitializing:', error);
        res.status(500).json({
            success: false,
            message: 'Error reinitializing connection',
            error: error.message
        });
    }
});

// Send message endpoint
app.post('/api/send', async (req, res) => {
    try {
        if (!isAuthenticated || !client) {
            return res.status(400).json({
                success: false,
                message: 'WhatsApp not authenticated'
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
        await client.sendMessage(chatId, message);
        
        res.json({
            success: true,
            message: 'Message sent successfully'
        });
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({
            success: false,
            message: 'Error sending message',
            error: error.message
        });
    }
});

// Send image endpoint (base64) — used for report screenshots
app.post('/api/send-image', async (req, res) => {
    try {
        if (!isAuthenticated || !client) {
            return res.status(400).json({ success: false, message: 'WhatsApp not authenticated' });
        }
        const { number, image, caption, filename } = req.body;
        if (!number || !image) {
            return res.status(400).json({ success: false, message: 'number and image (base64) are required' });
        }
        const chatId = number.includes('@c.us') ? number : `${number}@c.us`;
        const b64 = image.includes(',') ? image.split(',')[1] : image; // strip data: prefix if present
        const media = new MessageMedia('image/png', b64, filename || 'report.png');
        await client.sendMessage(chatId, media, { caption: caption || '' });
        res.json({ success: true, message: 'Image sent' });
    } catch (error) {
        console.error('Error sending image:', error);
        res.status(500).json({ success: false, message: 'Error sending image', error: error.message });
    }
});

// Allow the Flask backend (and large base64 images) through
app.use((req, res, next) => { next(); });

const PORT = 2786;

app.listen(PORT, () => {
    console.log(`OpenWA server running on port ${PORT}`);
    initializeWhatsApp();
});

process.on('SIGINT', () => {
    console.log('Shutting down...');
    if (client) {
        client.destroy();
    }
    process.exit(0);
});