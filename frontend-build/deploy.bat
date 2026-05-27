@echo off
echo.
echo ===================================
echo   ReportFlow Frontend Deployment
echo ===================================
echo.

echo Step 1: Open Cloudflare Pages
echo URL: https://pages.cloudflare.com
start https://pages.cloudflare.com

echo.
echo Step 2: Click "Create a project" then "Upload assets"
echo.
echo Step 3: Upload the following file:
echo   - index.html
echo.
echo Optional: Upload these files for enhanced security:
echo   - _headers (for security headers)
echo   - wrangler.toml (for advanced config)
echo.

pause

echo.
echo Step 4: After deployment, configure API URL:
echo   1. Visit your deployed site
echo   2. Click "⚙ API Config" (top-right)
echo   3. Enter backend URL:
echo      - Local: http://localhost:5001
echo      - Network: http://YOUR_LOCAL_IP:5001
echo.

echo ✅ Deployment guide complete!
echo.
echo 📁 Files ready for upload:
dir /b index.html _headers wrangler.toml
echo.
pause