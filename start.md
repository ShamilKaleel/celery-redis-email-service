# 🚀 Email Service with UV + Celery + Redis

## 📋 Prerequisites

- [UV](https://docs.astral.sh/uv/) - Ultra-fast Python package manager
- Docker & Docker Compose (for containerized setup)
- Redis (local or containerized)

## 🛠️ Install UV

### On macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### On Windows:
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Verify Installation:
```bash
uv --version
```

## 🏗️ Project Setup

### 1. Create Project Directory
```bash
mkdir email-project
cd email-project
```

### 2. Create All Project Files
Create the files from the artifacts above:
- `pyproject.toml`
- `.python-version` 
- `main.py`
- `celery_app.py`
- `tasks.py`
- `docker-compose.yml`
- `Dockerfile`
- `.env`

### 3. Initialize UV Project
```bash
# UV will automatically detect pyproject.toml and create virtual environment
uv sync
```

This command will:
- ✅ Create a virtual environment
- ✅ Install Python 3.11 (from .python-version)
- ✅ Install all dependencies from pyproject.toml
- ✅ Create uv.lock file for reproducible builds

## 🐳 Quick Start with Docker (Recommended)

### 1. Build and Start All Services
```bash
docker-compose up --build
```

### 2. Check Services are Running
```bash
docker-compose ps
```

You should see:
- ✅ `email_server` (FastAPI) on port 8000
- ✅ `email_celery_worker` (background processor)  
- ✅ `email_redis` (message queue)

### 3. Test the API
```bash
curl http://localhost:8000/
```

## 💻 Local Development with UV

### 1. Start Redis
```bash
# Option A: Use Docker
docker run -d -p 6379:6379 --name redis redis:alpine

# Option B: Install Redis locally (macOS)
brew install redis
redis-server
```

### 2. Start Celery Worker (Terminal 1)
```bash
uv run celery -A celery_app worker --loglevel=INFO
```

### 3. Start FastAPI Server (Terminal 2)
```bash
uv run uvicorn main:app --reload --port 8000
```

## 🧪 Testing the Email Service

### Create Test Script
```python
# test_email_service.py
import requests
import json

BASE_URL = "http://localhost:8000"

# Test single email
response = requests.post(f"{BASE_URL}/send-email", json={
    "recipient_email": "test@example.com",
    "subject": "Test from UV setup!",
    "message": "Hello from UV + Celery + Redis!"
})

print("Response:", json.dumps(response.json(), indent=2))
task_id = response.json()["task_id"]

# Check progress
import time
for i in range(10):
    status_response = requests.get(f"{BASE_URL}/task/{task_id}")
    status = status_response.json()
    print(f"Check {i+1}: {status['status']}")
    if status["status"] == "COMPLETED":
        print("✅ Email sent successfully!")
        break
    time.sleep(1)
```

### Run Test
```bash
uv run python test_email_service.py
```

## 📊 UV Commands Cheat Sheet

### Package Management
```bash
# Add new dependency
uv add fastapi

# Add development dependency  
uv add --dev pytest

# Remove dependency
uv remove package-name

# Update all dependencies
uv sync --upgrade

# Show installed packages
uv pip list
```

### Project Management
```bash
# Create new project
uv init my-project

# Sync dependencies (like npm install)
uv sync

# Run commands in virtual environment
uv run python script.py
uv run uvicorn main:app --reload

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### Python Version Management
```bash
# Install specific Python version
uv python install 3.11

# Set project Python version
echo "3.11" > .python-version

# List available Python versions
uv python list
```

## 🔍 Key UV Advantages

### ⚡ **Speed Comparison:**
```bash
# Traditional pip (slow)
pip install -r requirements.txt  # ~30 seconds

# UV (ultra-fast)
uv sync                          # ~3 seconds
```

### 🔒 **Dependency Resolution:**
- UV creates `uv.lock` for **exact reproducible builds**
- **Much faster** dependency resolution than pip
- **Better conflict detection**

### 🎯 **Project Isolation:**
- Automatic virtual environment creation
- **No more `pip install` in wrong environment**
- Project-specific Python versions

## 📈 Performance Monitoring

### Check Queue Length
```bash
curl http://localhost:8000/queue-status
```

### Monitor Docker Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery_worker
```

### Redis Monitoring
```bash
# Connect to Redis container
docker exec -it email_redis redis-cli

# Check queue length
LLEN celery

# List all keys
KEYS *

# Monitor commands in real-time
MONITOR
```

## 🛠️ Customization

### Add Real Email Sending

1. **Update .env file:**
```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

2. **Install email dependencies:**
```bash
uv add secure-smtplib
```

3. **Uncomment real email function in tasks.py**

### Scale Workers
```bash
# Add more workers to docker-compose.yml
docker-compose up --scale celery_worker=3
```

## 🧹 Cleanup

### Stop Services
```bash
docker-compose down
```

### Remove All Data
```bash
docker-compose down -v  # Removes Redis data volume
```

### Clean UV Environment
```bash
# Remove virtual environment
rm -rf .venv

# Recreate clean environment
uv sync
```

## 🆚 UV vs Traditional Setup

| Feature | Traditional (pip) | UV |
|---------|------------------|-----|
| **Install Speed** | 30+ seconds | 3 seconds |
| **Dependency Resolution** | Slow, sometimes incorrect | Fast, always correct |
| **Lock Files** | Manual (requirements.txt) | Automatic (uv.lock) |
| **Python Management** | Manual | Built-in |
| **Virtual Environments** | Manual creation | Automatic |
| **Project Isolation** | Manual | Automatic |

## 🎯 Next Steps

1. **Add Authentication** to email endpoints
2. **Implement Email Templates** with Jinja2
3. **Add Email Scheduling** for delayed sending
4. **Set up Monitoring** with Prometheus/Grafana
5. **Add Rate Limiting** to prevent abuse

UV makes Python project management **10x faster and more reliable**! 🚀