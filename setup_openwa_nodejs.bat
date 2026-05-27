@echo off
echo Setting up OpenWA directly with Node.js...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Node.js not found. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found
echo.

REM Create OpenWA directory
if not exist "openwa-server" mkdir openwa-server
cd openwa-server

REM Initialize npm project if not exists
if not exist "package.json" (
    echo Creating Node.js project...
    echo { "name": "openwa-server", "version": "1.0.0", "main": "server.js" } > package.json
)

REM Install OpenWA
echo Installing OpenWA...
npm install @open-wa/wa-automate express cors

REM Create server.js
echo Creating OpenWA server...
echo const { create, Client } = require('@open-wa/wa-automate'); > server.js
echo const express = require('express'); >> server.js
echo const cors = require('cors'); >> server.js
echo. >> server.js
echo const app = express(); >> server.js
echo app.use(cors()); >> server.js
echo app.use(express.json()); >> server.js
echo. >> server.js
echo let client = null; >> server.js
echo. >> server.js
echo // Health check >> server.js
echo app.get('/api/health', (req, res) =^> res.json({ status: 'ok' })); >> server.js
echo. >> server.js
echo // Get QR code >> server.js
echo app.get('/api/qr', (req, res) =^> { >> server.js
echo   if (client) { >> server.js
echo     res.json({ connected: true }); >> server.js
echo   } else { >> server.js
echo     res.json({ error: 'Client not initialized' }); >> server.js
echo   } >> server.js
echo }); >> server.js
echo. >> server.js
echo // Start server >> server.js
echo create({ >> server.js
echo   sessionId: 'reportflow', >> server.js
echo   qrTimeout: 0, >> server.js
echo   authTimeout: 0, >> server.js
echo   restartOnCrash: true, >> server.js
echo   cacheEnabled: false, >> server.js
echo }).then(c =^> { >> server.js
echo   client = c; >> server.js
echo   console.log('OpenWA client ready'); >> server.js
echo }).catch(err =^> console.error('Error:', err)); >> server.js
echo. >> server.js
echo app.listen(2785, () =^> console.log('OpenWA server running on port 2785')); >> server.js

echo ✅ OpenWA server created
echo.
echo Starting OpenWA server...
echo You can stop it with Ctrl+C
echo.
node server.js