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

# Database configuration - Azure SQL Database
# Use Azure SQL for persistent storage
def get_database_url():
    # Check for full DATABASE_URL first (for Railway environment variables)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # Build from individual components (fallback)
    server = os.environ.get('DB_SERVER', 'skapaserver.database.windows.net')
    database = os.environ.get('DB_NAME', 'VDR')
    username = os.environ.get('DB_USER', 'CloudSA65310c01')
    password = os.environ.get('DB_PASSWORD', '')
    
    if password:
        # SQL Server connection string for SQLAlchemy with pymssql (Railway compatible)
        return f"mssql+pymssql://{username}:{password}@{server}/{database}?charset=utf8"
    else:
        # Fallback to in-memory for development
        return 'sqlite:///:memory:'

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable file uploads when using Azure SQL (persistent storage)
AZURE_SQL_MODE = 'mssql' in app.config['SQLALCHEMY_DATABASE_URI']
RAILWAY_MODE = os.environ.get('RAILWAY_STATIC_URL') is not None and not AZURE_SQL_MODE

db.init_app(app)
with app.app_context():
    db.create_all()

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
    app.run(host='0.0.0.0', port=port, debug=debug)
