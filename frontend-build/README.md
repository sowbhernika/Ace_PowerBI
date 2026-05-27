# ReportFlow Frontend - Cloud Deployment

This is the standalone frontend for ReportFlow Power BI to WhatsApp automation system.

## 🚀 Quick Setup

### Option 1: Cloudflare Pages (Recommended)

1. **Create Cloudflare Pages Project**
   - Go to [Cloudflare Pages](https://pages.cloudflare.com)
   - Click "Create a project"
   - Choose "Upload assets" for direct deployment
   - Upload the `index.html` file

2. **Configure Custom Domain (Optional)**
   - In Cloudflare Pages dashboard, go to "Custom domains"
   - Add your domain and configure DNS

### Option 2: Direct File Upload

1. **Upload to any static hosting**:
   - Netlify: Drag & drop `index.html` to [Netlify Drop](https://app.netlify.com/drop)
   - Vercel: Use `npx vercel` command
   - GitHub Pages: Push to a GitHub repo and enable Pages

## ⚙️ Configuration

1. **Access the deployed frontend**
2. **Click "⚙ API Config" button** (top-right corner)
3. **Set Backend URL**: Enter your local server address
   - Local: `http://localhost:5001`
   - Network: `http://YOUR_LOCAL_IP:5001`
   - Public: `http://YOUR_PUBLIC_IP:5001` (with firewall rules)

## 🔧 Backend Requirements

The backend must be running locally with CORS enabled:

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app, origins=["*"])  # Already configured
```

## 🌐 Access from Anywhere

1. **Local Network**: Use your computer's local IP
   ```
   http://192.168.1.100:5001
   ```

2. **Public Internet**: 
   - Configure port forwarding (port 5001)
   - Use your public IP or domain
   - **Security Warning**: Only for trusted users

## 📱 Features

- ✅ Full ReportFlow functionality
- ✅ Report management
- ✅ Manager CRUD operations  
- ✅ Scheduling system
- ✅ Send history tracking
- ✅ WhatsApp & Power BI setup
- ✅ Bulk operations
- ✅ CSV import/export
- ✅ Real-time status updates

## 🔒 Security

- HTTPS enforced on Cloudflare Pages
- CSP headers configured
- API URL stored locally (localStorage)
- No sensitive data in frontend

## 🆘 Troubleshooting

**"Failed to connect to API"**
- Verify backend is running on specified port
- Check CORS is enabled
- Verify firewall allows the port
- Test API URL directly in browser

**"Mixed Content Error"**
- Use HTTPS for both frontend and backend
- Or use HTTP for both (local only)

## 📁 File Structure

```
frontend-build/
├── index.html          # Complete standalone frontend
├── _headers            # Cloudflare security headers
├── wrangler.toml       # Cloudflare configuration
└── README.md           # This file
```

## 🔄 Updates

To update the frontend:
1. Modify `index.html`
2. Re-upload to your hosting provider
3. Clear browser cache if needed