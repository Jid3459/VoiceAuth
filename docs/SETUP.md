
### `docs/SETUP.md`

```markdown
# Setup Guide

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 14 or higher
- **RAM**: Minimum 8GB (16GB recommended for SpeechBrain)
- **Storage**: 5GB free space

### Software Installation

#### Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# macOS
brew install python@3.10

# Windows
Download from python.org

Node.js
Bash

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# macOS
brew install node@18

# Windows
Download from nodejs.org
PostgreSQL
Bash

# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@14

# Windows
Download from postgresql.org
Database Setup
1. Start PostgreSQL
Bash

# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql@14
2. Create Database
Bash

sudo -u postgres psql

# In psql:
CREATE DATABASE voice_auth_db;
CREATE USER voice_auth_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE voice_auth_db TO voice_auth_user;
\q
3. Verify Connection
Bash

psql -U voice_auth_user -d voice_auth_db -h localhost
Backend Setup
1. Clone Repository
Bash

git clone <repository-url>
cd voice-auth-ordering/backend
2. Create Virtual Environment
Bash

python3 -m venv venv

# Activate
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
3. Install Dependencies
Bash

pip install --upgrade pip
pip install -r requirements.txt
Note: SpeechBrain and PyTorch will download ~2GB of dependencies.

4. Configure Environment
Bash

cp .env.example .env
Edit .env:

env

DATABASE_URL=postgresql://voice_auth_user:your_secure_password@localhost:5432/voice_auth_db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SIMILARITY_THRESHOLD_STRONG=0.75
SIMILARITY_THRESHOLD_WEAK=0.50
5. Run Migrations
Tables are auto-created on first run via SQLAlchemy.

6. Start Backend Server
Bash

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Server will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

Frontend Setup
1. Navigate to Frontend
Bash

cd ../frontend
2. Install Dependencies
Bash

npm install
3. Configure Environment (Optional)
Create .env.local:

env

VITE_API_BASE_URL=http://localhost:8000
4. Start Development Server
Bash

npm run dev
Frontend will be available at: http://localhost:5173

First Time Use
1. Access Frontend
Open browser: http://localhost:5173

2. Register Account
Click "Register"
Enter username, email, password
Click "Register"
3. Enroll Voice
Allow microphone access when prompted
Click "Start Recording"
Speak clearly for 5-10 seconds (e.g., "My voice is my password")
Click "Stop Recording"
Wait for enrollment confirmation
4. Place Order
Enter product query (e.g., "Buy iPhone 13")
Click "Start Recording"
Speak your query or any phrase
Click "Stop Recording"
View authentication results and decision
Testing
Backend Tests
Bash

cd backend
source venv/bin/activate
pytest tests/ -v
Frontend Tests
Bash

cd frontend
npm test
Production Deployment
Backend (Gunicorn + Nginx)
Bash

# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Frontend (Build)
Bash

npm run build
# Serve 'dist' folder with nginx or any static server
Environment Variables
Change SECRET_KEY to strong random string
Update DATABASE_URL with production credentials
Set CORS origins to production domains
Troubleshooting
SpeechBrain Model Download Issues
Bash

# Manually download model
python -c "from speechbrain.pretrained import EncoderClassifier; EncoderClassifier.from_hparams(source='speechbrain/spkrec-ecapa-voxceleb')"
PostgreSQL Connection Error
Bash

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U voice_auth_user -d voice_auth_db -h localhost
Microphone Access Denied
Enable HTTPS for production (required for getUserMedia API)
Check browser permissions
Port Already in Use
Bash

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
Support
For issues, please check:

Logs in terminal
Browser console
PostgreSQL logs: /var/log/postgresql/