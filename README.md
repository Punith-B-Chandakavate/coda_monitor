# 🔒 Coda Security Monitor

A comprehensive security monitoring solution for Coda documents that automatically detects sensitive data, sends real-time alerts, and provides remediation workflows.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [AI Tools Used](#ai-tools-used)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Detection Rules](#detection-rules)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Extensibility](#extensibility)



## ✨ Features

### Core Functionality
- ✅ **Automated Document Scanning** - Hourly scans of all Coda documents
- ✅ **Sensitive Data Detection** - Pattern-based detection of PII, credentials, and sensitive information
- ✅ **Real-time Slack Alerts** - Instant notifications for critical findings
- ✅ **Remediation Workflow** - One-click resolution, ignoring, or marking issues in progress
- ✅ **Web Dashboard** - Real-time dashboard with auto-refresh capabilities
- ✅ **Audit Logging** - Complete scan history and issue tracking
- ✅ **Docker Support** - Easy deployment with Docker Compose
- ✅ **REST API** - Programmatic access to all features

### Security Patterns Detected
| Pattern | Severity | Description |
|---------|----------|-------------|
| Email Address | MEDIUM | Standard email format |
| Credit Card | CRITICAL | 13-16 digit numbers |
| SSN | CRITICAL | XXX-XX-XXXX format |
| Phone Number | MEDIUM | US/International formats |
| IP Address | MEDIUM | IPv4 addresses |
| API Key | HIGH | 32+ character strings |
| Password | HIGH | Password in plain text |
| Bank Account | HIGH | 10-12 digit numbers |
| Date of Birth | MEDIUM | Various date formats |

## 🏗 Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Coda API   │◄────│   APScheduler│     │   Django    │
│             │     │  (Scheduler) │     │   Server    │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Pattern     │     │   SQLite     │     │   Slack     │
│ Detector    │────►│  (Database)  │────►│   Alerts    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                          
       ▼                                          
┌─────────────┐     ┌──────────────┐             
│   HTML      │     │   REST API   │             
│  Dashboard  │◄────│  Endpoints   │             
└─────────────┘     └──────────────┘             
```

## 🤖 AI Tools Used

This project was developed using a combination of AI tools to accelerate development and ensure code quality:

### **DeepSeek AI**
**Usage & Contribution:**
- **Initial Architecture Design**: DeepSeek helped design the modular architecture, suggesting the separation of concerns between Coda client, pattern detection, and alert services
- **Pattern Recognition Algorithms**: Developed the regex patterns for sensitive data detection, including credit card validation and SSN matching
- **Docker Configuration**: Created production-ready Dockerfiles and docker-compose configurations
- **Error Handling Strategies**: Implemented comprehensive error handling and logging mechanisms
- **Database Schema Design**: Designed the Django models with proper relationships and indexing strategies

**Why DeepSeek?**
- Excellent at understanding complex system requirements
- Superior code generation with attention to error handling
- Strong understanding of security patterns and best practices
- Cost-effective for large-scale code generation

### **ChatGPT (OpenAI)**
**Usage & Contribution:**
- **Frontend Dashboard**: Developed the responsive HTML/CSS dashboard with real-time updates
- **Slack Integration**: Implemented the Slack webhook integration with rich formatting and buttons
- **API Endpoints**: Created RESTful API endpoints with proper request/response handling
- **Testing Framework**: Wrote unit tests and debugging scripts
- **Documentation**: Generated comprehensive README and inline code comments

**Why ChatGPT?**
- Excellent at frontend development and UI/UX design
- Strong at writing clean, readable code with good documentation
- Great at explaining complex concepts in documentation
- Versatile in handling multiple programming paradigms

### **Development Process with AI**

1. **Planning Phase (DeepSeek)**
   - System architecture design
   - Database schema planning
   - API endpoint design

2. **Development Phase (Both)**
   - Backend logic implementation (DeepSeek)
   - Frontend dashboard development (ChatGPT)
   - Integration and testing (Both)

3. **Optimization Phase (Both)**
   - Performance tuning
   - Security hardening
   - Documentation refinement

### **Benefits of Using AI in This Project**

- ⚡ **Rapid Development**: Complete working solution in days instead of weeks
- 🎯 **Best Practices**: AI suggested industry-standard patterns and practices
- 🐛 **Bug Reduction**: AI-assisted code review caught potential issues early
- 📚 **Comprehensive Documentation**: Auto-generated documentation with examples
- 🔧 **Easy Maintenance**: Modular code structure with clear separation of concerns

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Coda account with API access
- Slack workspace (optional, for alerts)

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd coda_monitor

# Configure environment variables
cp .env.example .env
# Edit .env with your Coda API token and Slack webhook

# Build and run with Docker Compose
docker-compose up -d

# Access the dashboard
open http://localhost:8000
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone <repository-url>
cd coda_monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Docker Commands

```bash
# Check container status
docker-compose ps

# Execute commands in container
docker exec -it coda-security-monitor python manage.py shell

# Backup database
docker cp coda-security-monitor:/app/db.sqlite3 ./backup.db

# View resource usage
docker stats coda-security-monitor
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: Coda API Configuration
CODA_API_TOKEN=your_coda_api_token_here

# Optional: Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url

# Django Configuration
DJANGO_SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### Getting Coda API Token

1. Log into [Coda](https://coda.io)
2. Go to Account Settings → API Tokens
3. Generate a new token
4. Copy the token to your `.env` file

### Setting Up Slack Webhook

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app or use existing
3. Enable Incoming Webhooks
4. Add webhook to your channel (e.g., `#all-coda-security-monitor`)
5. Copy the webhook URL to your `.env` file

## 🎯 Detection Rules

### Customizing Detection Patterns

Add new patterns in `monitor/utils/pattern_detector.py`:

```python
PATTERNS = {
    'CUSTOM_PATTERN': {
        'regex': r'your-regex-here',
        'severity': 'HIGH',  # LOW, MEDIUM, HIGH, CRITICAL
        'description': 'Pattern description'
    }
}
```

### Severity Levels

- **CRITICAL**: Credit cards, SSNs - Immediate action required
- **HIGH**: API keys, passwords - Urgent remediation
- **MEDIUM**: Emails, phone numbers - Monitor and review
- **LOW**: General information - Informational only

## 📖 Usage Guide

### Web Dashboard

1. **Access Dashboard**: `http://localhost:8000`
2. **View Summary Cards**: Overview of documents and issues
3. **Filter Issues**: By severity, status, or document
4. **Take Action**: Resolve, ignore, or mark issues in progress
5. **Trigger Manual Scan**: Click "Trigger Scan" button

### API Endpoints

```bash
# Get dashboard summary
curl http://localhost:8000/api/summary/

# List all documents
curl http://localhost:8000/api/documents/

# Get detected issues
curl http://localhost:8000/api/issues/

# Filter issues by severity
curl http://localhost:8000/api/issues/?severity=CRITICAL

# Remediate an issue
curl -X POST http://localhost:8000/api/remediate/ \
  -H "Content-Type: application/json" \
  -d '{"issue_id": 123, "action": "resolve", "note": "Fixed"}'

# Trigger manual scan
curl -X POST http://localhost:8000/api/trigger-scan/
```

### Admin Interface

Access Django admin at `http://localhost:8000/admin` to:
- Manage documents
- Review all issues
- View scan logs
- Export data

## 🔧 Troubleshooting

### Common Issues

**Issue**: Coda API authentication fails
```bash
# Solution: Verify API token
python manage.py shell
>>> from monitor.utils.coda_client import CodaAPIClient
>>> client = CodaAPIClient()
>>> print(client.list_documents())
```

**Issue**: Slack notifications not working
```bash
# Test Slack connection
python test_slack_alert.py
```

**Issue**: Database errors
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

**Issue**: Docker container won't start
```bash
# Check logs
docker-compose logs web

# Check port availability
netstat -an | findstr 8000
```

### Logging

Logs are stored in `logs/monitor.log` with rotation (10MB per file, 5 backups).

View real-time logs:
```bash
# Docker
docker-compose logs -f web

# Local
tail -f logs/monitor.log  # Linux/Mac
Get-Content logs\monitor.log -Wait  # Windows PowerShell
```

## 🔌 Extensibility

### Adding New Remediation Actions

Modify `monitor/tasks.py`:

```python
def remediate_issue_sync(issue_id: int, action: str, note: str = ""):
    if action == 'archive':
        issue.status = 'ARCHIVED'
        # Custom logic here
```

### Adding New Alert Channels

Extend `monitor/utils/alert_service.py`:

```python
def send_email_alert(self, message: str):
    # Implement email logic
    pass

def send_teams_alert(self, message: str):
    # Implement Microsoft Teams logic
    pass
```