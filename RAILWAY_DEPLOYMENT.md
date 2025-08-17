# VDR Railway Deployment Guide

## 🚂 Railway-Specific Fixes Applied

This version of the VDR has been specifically modified to work with Railway's deployment environment:

### ✅ **Fixed Issues:**

1. **Database Path Problem:**
   - **Problem:** Railway has a read-only filesystem, SQLite couldn't write to `/app/src/database/`
   - **Solution:** Database now uses `/tmp/vdr_app.db` (writable on Railway)
   - **Environment Variable:** `DATABASE_URL` (optional override)

2. **File Upload Directory:**
   - **Problem:** Upload directory wasn't writable on Railway
   - **Solution:** Uploads now go to `/tmp/vdr_uploads/`
   - **Environment Variable:** `UPLOADS_DIR` (optional override)

3. **Dynamic Configuration:**
   - Uses environment variables for all paths
   - Automatically creates necessary directories
   - Railway-compatible port configuration

## 🚀 **Railway Deployment Steps:**

### **1. Upload to GitHub:**
```bash
# Create new repository on GitHub
# Upload all files from this package
git init
git add .
git commit -m "Initial VDR commit - Railway compatible"
git remote add origin https://github.com/yourusername/vdr-railway.git
git push -u origin main
```

### **2. Deploy on Railway:**
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your VDR repository
4. Railway will automatically detect Flask
5. **No additional configuration needed!**

### **3. Optional Environment Variables:**
Set these in Railway dashboard if needed:
- `DATABASE_URL` - Custom database path (default: `sqlite:///tmp/vdr_app.db`)
- `UPLOADS_DIR` - Custom uploads directory (default: `/tmp/vdr_uploads`)
- `SECRET_KEY` - Custom secret key for sessions
- `FLASK_ENV` - Set to `production` for production mode

## 🔧 **Technical Changes Made:**

### **main.py Changes:**
```python
# OLD (Railway incompatible):
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

# NEW (Railway compatible):
database_path = os.environ.get('DATABASE_URL', f"sqlite:///tmp/vdr_app.db")
app.config['SQLALCHEMY_DATABASE_URI'] = database_path

# Create uploads directory in /tmp for Railway
uploads_dir = os.environ.get('UPLOADS_DIR', '/tmp/vdr_uploads')
os.makedirs(uploads_dir, exist_ok=True)
```

### **documents.py Changes:**
```python
# OLD (Railway incompatible):
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

# NEW (Railway compatible):
UPLOAD_FOLDER = os.environ.get('UPLOADS_DIR', '/tmp/vdr_uploads')
```

## ⚠️ **Important Notes:**

1. **Data Persistence:**
   - Railway's `/tmp` directory is ephemeral
   - Data will be lost on app restarts/deployments
   - For production, consider upgrading to PostgreSQL

2. **File Uploads:**
   - Uploaded files are stored in `/tmp/vdr_uploads/`
   - Files will be lost on app restarts
   - Consider using cloud storage (AWS S3, etc.) for production

3. **Database Migration:**
   - For production use, migrate to Railway's PostgreSQL addon
   - Update `DATABASE_URL` environment variable accordingly

## 🎯 **Production Recommendations:**

### **Upgrade to PostgreSQL:**
1. Add PostgreSQL plugin in Railway dashboard
2. Update `DATABASE_URL` environment variable
3. Install `psycopg2` in requirements.txt
4. Database tables will be created automatically

### **Cloud File Storage:**
1. Integrate AWS S3 or similar
2. Update document upload/download logic
3. Set `UPLOADS_DIR` to cloud storage path

## ✅ **Verification:**

After deployment, your VDR should be accessible at:
`https://your-app.railway.app`

**Default Login:**
- Username: `admin`
- Password: `admin123`

**Test These Features:**
- User registration/login
- Document upload (will work but files are temporary)
- Q&A system
- Folder creation

## 🐛 **Troubleshooting:**

**If deployment still fails:**
1. Check Railway build logs
2. Verify all files are uploaded to GitHub
3. Ensure `requirements.txt` is present
4. Check Railway environment variables

**Common Issues:**
- **Port binding:** App automatically uses Railway's `PORT` environment variable
- **Database creation:** Database and tables are created automatically on first run
- **File permissions:** All paths use `/tmp` which is writable on Railway

Your VDR is now Railway-compatible and ready for deployment! 🎉

