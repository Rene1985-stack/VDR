# VDR Deployment Instructions

## 🚀 Quick Deploy to Railway (Recommended)

1. **Upload to GitHub:**
   - Create a new repository on GitHub
   - Upload all files from this zip to your repository
   - Commit and push

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your VDR repository
   - Railway will automatically detect Flask and deploy
   - Your VDR will be live at `https://your-app.railway.app`

## 🔧 Alternative Deployments

### Heroku
```bash
heroku create your-vdr-app
git push heroku main
```

### DigitalOcean App Platform
- Connect GitHub repository
- Build Command: `pip install -r requirements.txt`
- Run Command: `python src/main.py`

## 📋 What's Included

- ✅ Complete Flask backend with all APIs
- ✅ Built React frontend (in src/static/)
- ✅ Database models and migrations
- ✅ User authentication system
- ✅ Document management
- ✅ Q&A system
- ✅ Folder organization
- ✅ Production-ready configuration

## 🔐 Default Accounts

After deployment, you can create accounts or use:
- **Username:** admin
- **Password:** admin123

## 🌐 Features

- Document upload/download
- Hierarchical folder system
- Q&A threads
- User management
- Admin panel
- Responsive design

## 📞 Support

The VDR is fully functional and ready for production use. All dependencies and configurations are included.

