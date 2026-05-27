# Update Frontend for ngrok

## Step 1: Get ngrok URL
Run in Command Prompt:
```
ngrok http 5000
```
Copy the https://xxxx.ngrok.io URL

## Step 2: Update frontend
Edit `frontend-build\index.html` line 394:

Change:
```javascript
let API_BASE_URL = localStorage.getItem('api_base_url') || 'http://103.130.205.113:5000';
```

To:
```javascript  
let API_BASE_URL = localStorage.getItem('api_base_url') || 'https://YOUR_NGROK_URL';
```

## Step 3: Redeploy to Netlify
1. Drag the updated `frontend-build` folder to Netlify again
2. It will update your existing site

## Alternative: Configure in browser
Instead of editing code, users can:
1. Visit your Netlify site
2. Click "⚙ API Config" 
3. Enter your ngrok URL: `https://xxxx.ngrok.io`
4. Click "Save & Test"