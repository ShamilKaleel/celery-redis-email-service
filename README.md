# 📧 Email Service with UV + Celery + Redis

A modern email service demonstrating **asynchronous background processing** using:
- 🚀 **[UV](https://docs.astral.sh/uv/)** - Ultra-fast Python package manager
- ⚡ **FastAPI** - Modern web framework  
- 🔄 **Celery** - Background task processing
- 📊 **Redis** - Message broker and result backend
- 🐳 **Docker** - Containerized deployment

## 🌟 Why This Stack?

### ⚡ **UV Benefits:**
- **10x faster** than pip
- **Automatic** virtual environments
- **Exact** dependency resolution with `uv.lock`
- **Built-in** Python version management
- **Zero-config** project setup

### 🔄 **Async Processing Benefits:**
- **Instant response** (0.1s vs 5-30s)
- **Multiple users** can send emails simultaneously  
- **Progress tracking** for long-running tasks
- **Reliable queue** management
- **Scalable** worker processes

## 🚀 Quick Start

### 1. **Install UV**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. **Clone & Setup**
```bash
# Create project directory
mkdir email-project && cd email-project

# Copy all project files (from the artifacts)
# Then run the automated setup:
chmod +x setup.sh
./setup.sh
```

### 3. **Test the Service**
```bash
uv run python test_email_service.py
```

## 📁 Project Structure

```
email-project/
├── pyproject.toml           # UV dependencies & config
├── .python-version          # Python version (3.11)
├── uv.lock                  # Exact dependency versions (auto-generated)
├── main.py                  # FastAPI web server
├── celery_app.py           # Celery configuration
├── tasks.py                # Background email tasks
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # UV-optimized container
├── .env                    # Environment variables
├── test_email_service.py   # Test script
└── setup.sh               # Automated setup script
```

## 🧪 API Examples

### **Send Single Email**
```bash
curl -X POST "http://localhost:8000/send-email" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "john@example.com",
    "subject": "Hello from UV + Celery!",
    "message": "This email was sent asynchronously using UV package manager!"
  }'
```

**Response (0.1 seconds):**
```json
{
  "task_id": "abc123-def456",
  "status": "PENDING",
  "message": "Email to john@example.com is being sent in background",
  "estimated_completion": "5-10 seconds"
}
```

### **Check Progress**
```bash
curl "http://localhost:8000/task/abc123-def456"
```

**Progressive Responses:**
```json
// After 2 seconds
{
  "task_id": "abc123-def456",
  "status": "PROGRESS",
  "meta": {
    "status": "Connecting to email server",
    "step": "3/6",
    "progress": 50
  }
}

// After 7 seconds  
{
  "task_id": "abc123-def456",
  "status": "COMPLETED",
  "result": {
    "recipient": "john@example.com",
    "message": "Email sent successfully!",
    "processing_time": "~7 seconds"
  }
}
```

### **Send Bulk Emails**
```bash
curl -X POST "http://localhost:8000/send-bulk-emails" \
  -H "Content-Type: application/json" \
  -d '{
    "email_list": ["alice@example.com", "bob@example.com", "charlie@example.com"],
    "subject": "Bulk Email with UV",
    "message": "Sent to multiple recipients using async processing!"
  }'
```

## 🔧 Development Workflow

### **Local Development with UV**

1. **Start Redis:**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

2. **Start Celery Worker:**
```bash
uv run celery -A celery_app worker --loglevel=INFO
```

3. **Start FastAPI Server:**
```bash
uv run uvicorn main:app --reload --port 8000
```

### **Docker Development**
```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Restart services  
docker-compose restart

# Stop services
docker-compose down
```

### **UV Commands**

```bash
# Install dependencies
uv sync

# Add new dependency
uv add fastapi

# Add dev dependency
uv add --dev pytest

# Run commands in UV environment
uv run python script.py
uv run uvicorn main:app --reload

# Show installed packages
uv pip list

# Update dependencies
uv sync --upgrade
```

## 📊 Performance Comparison

| Method | Response Time | User Experience | Scalability |
|--------|---------------|-----------------|-------------|
| **Synchronous** | 5-30 seconds | ❌ Browser timeout | ❌ 1 user at a time |
| **UV + Celery** | 0.1 seconds | ✅ Instant response | ✅ Many users simultaneously |

### **Real Example:**

```python
# ❌ Synchronous (blocks for 5 seconds)
@app.post("/send-email-sync")
def send_email_sync(email_data):
    send_email(email_data)  # Blocks here!
    return {"status": "sent"}

# ✅ Asynchronous (returns in 0.1 seconds)  
@app.post("/send-email")
def send_email_async(email_data):
    task = send_email_task.delay(email_data)  # Non-blocking!
    return {"task_id": task.id, "status": "pending"}
```

## 🔍 Monitoring & Debugging

### **Check Queue Status**
```bash
curl http://localhost:8000/queue-status
```

### **Monitor Redis**
```bash
# Connect to Redis container
docker exec -it email_redis redis-cli

# Check queue length
LLEN celery

# Monitor real-time commands
MONITOR
```

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery_worker

# UV virtual environment logs
uv run celery -A celery_app worker --loglevel=DEBUG
```

## 🛠️ Customization

### **Add Real Email Sending**

1. **Update `.env`:**
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

3. **Update `tasks.py`:**
```python
# Uncomment the send_real_email function
def send_real_email(recipient, subject, message):
    # Implementation provided in tasks.py
```

### **Scale Workers**
```bash
# Add more workers
docker-compose up --scale celery_worker=3

# Or update docker-compose.yml for permanent scaling
```

### **Add Authentication**
```bash
uv add python-jose[cryptography] passlib[bcrypt]
```

## 🚀 Production Deployment

### **Environment Variables**
```bash
# .env for production
REDIS_HOST=your-redis-host
REDIS_PORT=6379
SENDER_EMAIL=noreply@yourcompany.com
SENDER_PASSWORD=your-secure-password
SMTP_SERVER=smtp.yourdomain.com
```

### **Docker Production**
```bash
# Build production image
docker build -t email-service:prod .

# Run with production settings
docker-compose -f docker-compose.prod.yml up
```

## 🆚 UV vs Traditional Setup

| Aspect | Traditional (pip) | UV |
|--------|------------------|-----|
| **Dependency Install** | `pip install -r requirements.txt` (30s) | `uv sync` (3s) |
| **Virtual Environment** | `python -m venv .venv && source .venv/bin/activate` | Automatic |
| **Lock Files** | Manual `pip freeze > requirements.txt` | Automatic `uv.lock` |
| **Python Version** | Manual pyenv/virtualenv management | `echo "3.11" > .python-version` |
| **Project Setup** | Multi-step manual process | `uv init` |
| **Dependency Resolution** | Can be incorrect/slow | Always correct & fast |

## 🐛 Troubleshooting

### **Common Issues:**

**"Connection refused to Redis"**
```bash
# Check if Redis is running
docker-compose ps redis

# Restart Redis
docker-compose restart redis
```

**"UV command not found"**
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

**"Tasks stuck in PENDING"**
```bash
# Check worker status
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker
```

**"Virtual environment issues"**
```bash
# Remove and recreate
rm -rf .venv
uv sync
```

## 📚 Learn More

- [UV Documentation](https://docs.astral.sh/uv/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install dependencies: `uv sync`
4. Make changes and test: `uv run python test_email_service.py`
5. Submit a pull request

## 📄 License

MIT License - feel free to use this project as a starting point for your own applications!

---

**Made with ❤️ using UV - The future of Python package management** 🚀