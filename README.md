# Virtual Data Room (VDR)

A complete Virtual Data Room application with document management, Q&A system, and folder organization.

## Features

- 🔐 **User Authentication** - Registration, login, admin roles
- 📁 **Document Management** - Upload, download, organize in folders
- ❓ **Q&A System** - Ask questions, provide answers, thread management
- 📂 **Folder Organization** - Hierarchical folder structure with breadcrumbs
- 👥 **Multi-user Support** - User accounts with different permission levels
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Tech Stack

- **Backend:** Flask, SQLAlchemy, SQLite
- **Frontend:** React, Tailwind CSS, Vite
- **Authentication:** Session-based with password hashing
- **File Storage:** Local filesystem with metadata in database

## Quick Start

### Local Development

1. **Backend Setup:**
   ```bash
   cd vdr-app
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python src/main.py
   ```

2. **Frontend Setup:**
   ```bash
   cd vdr-frontend
   npm install
   npm run dev
   ```

### Production Deployment

The application is ready for deployment on:
- Railway
- Heroku  
- DigitalOcean App Platform
- Vercel (frontend) + Railway (backend)

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

## Environment Variables

- `PORT` - Server port (default: 5002)
- `FLASK_ENV` - Set to 'production' for production deployment

## Default Accounts

- **Admin:** admin / admin123
- **User:** ReneDenRonde / SK2050885Ronde!

## Project Structure

```
vdr-app/
├── src/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── database/        # SQLite database
│   └── static/          # Built frontend files
├── requirements.txt     # Python dependencies
├── Procfile            # Heroku deployment
└── README.md
```

## API Endpoints

- `/api/register` - User registration
- `/api/login` - User login
- `/api/logout` - User logout
- `/api/documents` - Document CRUD operations
- `/api/folders` - Folder management
- `/api/questions` - Q&A system

## License

MIT License - Feel free to use and modify for your needs.

