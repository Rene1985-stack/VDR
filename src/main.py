import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.documents import documents_bp
from src.routes.qa import qa_bp
from src.routes.folders import folders_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, supports_credentials=True)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(documents_bp, url_prefix='/api')
app.register_blueprint(qa_bp, url_prefix='/api')
app.register_blueprint(folders_bp, url_prefix='/api')

# Database configuration - Individual SQL environment variables (like Node.js project)
def get_database_url():
    # Use individual SQL environment variables (preferred method)
    server = os.environ.get('SQL_SERVER')
    database = os.environ.get('SQL_DATABASE') 
    username = os.environ.get('SQL_USER')
    password = os.environ.get('SQL_PASSWORD')
    port = os.environ.get('SQL_PORT', '1433')
    
    # Check if all required SQL variables are present
    if all([server, database, username, password]):
        # Enhanced SQL Server connection string with Azure SQL options (matching Node.js config)
        # Equivalent to Node.js: encrypt: true, trustServerCertificate: false, connectionTimeout: 30000
        connection_params = [
            "charset=utf8",
            "encrypt=yes",                    # encrypt: true
            "TrustServerCertificate=no",      # trustServerCertificate: false  
            "Connection+Timeout=30",          # connectionTimeout: 30000ms = 30s
            "Login+Timeout=30",               # Additional login timeout
            "Timeout=30"                      # Query timeout
        ]
        
        params_string = "&".join(connection_params)
        connection_url = f"mssql+pymssql://{username}:{password}@{server}:{port}/{database}?{params_string}"
        
        print(f"🔗 Connecting to Azure SQL with enhanced options:")
        print(f"   Server: {server}")
        print(f"   Database: {database}")
        print(f"   User: {username}")
        print(f"   Options: encrypt=yes, trustServerCertificate=no, timeout=30s")
        
        return connection_url
    
    # Fallback: Check for full DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print("🔗 Using DATABASE_URL fallback")
        return database_url
    
    # Final fallback: in-memory for development
    print("⚠️  No SQL variables found, using in-memory database for development")
    return 'sqlite:///:memory:'

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable file uploads when using Azure SQL (persistent storage)
AZURE_SQL_MODE = 'mssql' in app.config['SQLALCHEMY_DATABASE_URI']
RAILWAY_MODE = os.environ.get('RAILWAY_STATIC_URL') is not None and not AZURE_SQL_MODE

db.init_app(app)
with app.app_context():
    try:
        print("🗄️  Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("🔍 Check your SQL environment variables and Azure SQL firewall settings")
        raise

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"🚀 Starting VDR on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

