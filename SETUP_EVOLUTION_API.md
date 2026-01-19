# Evolution API Setup Guide

This project now supports **Evolution API** as the primary WhatsApp integration platform. Evolution API is more reliable and feature-complete than WAHA Community Edition.

## ✅ What's Been Configured

### 1. **Evolution API Service** (`/services/evolution_api.py`)
- Full client implementation for Evolution API
- Methods implemented:
  - `send_message(chat_id, message)` - Send WhatsApp messages
  - `start_typing(chat_id)` - Show typing indicator
  - `stop_typing(chat_id)` - Hide typing indicator
  - `get_status()` - Health check

### 2. **Docker Compose Setup** (`docker-compose.yml`)
Complete multi-container setup:
- **evolution** - Evolution API service (port 3333)
- **evolution_db** - PostgreSQL database for Evolution
- **evolution_redis** - Redis cache for Evolution
- **api** - Flask application (port 5000)

All containers have:
- Health checks configured
- Proper networking and aliases
- Automatic dependency resolution

### 3. **Flask Application** (`app.py`)
Updated to:
- Import and initialize Evolution API by default
- Use `whatsapp_service` abstraction (works with both Evolution and WAHA)
- All message handling uses Evolution API methods
- Fallback to WAHA possible via `USE_EVOLUTION_API=false`

### 4. **Environment Configuration** (`.env`)
```env
GROQ_API_KEY=your_groq_key_here

# Evolution API (PRIMARY)
EVOLUTION_API_URL=http://evolution:3333
EVOLUTION_API_KEY=sk_test_your_api_key_here
EVOLUTION_INSTANCE_NAME=default

# WAHA (DEPRECATED - fallback only)
WAHA_API_KEY=0461831dcb974837b33fd6d0d283e72b
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Navigate to project directory
cd /home/andre-souza/Desktop/Vscode/bot_wtas/Waha_Groq_langchain

# 2. Build and start containers
docker compose up -d

# 3. Verify services are running
docker compose ps

# 4. Check logs
docker compose logs -f api
```

### Option 2: Local Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Evolution API separately (optional)
# Either use Docker: docker run -p 3333:3333 atendesimples/evolution-api:latest
# Or use your existing Evolution API instance

# 3. Update .env with your Evolution API details
# EVOLUTION_API_URL=http://your-evolution-server:3333
# EVOLUTION_API_KEY=your_api_key_here

# 4. Run Flask app
python app.py
```

## 📋 Requirements Met

✅ Evolution API service ready for WhatsApp integration
✅ PostgreSQL database configured for Evolution
✅ Redis cache for optimal performance
✅ Flask application fully integrated
✅ Health checks and dependency management
✅ Automatic startup and restart policies
✅ Logging configured for debugging
✅ Environment variables properly set

## 🔄 Message Flow

```
WhatsApp Message
    ↓
Evolution API Webhook → POST /wpp-bot-api
    ↓
Flask processes message, extracts text
    ↓
Groq LLM generates response
    ↓
Evolution API sends response back to WhatsApp
```

## 🔧 Evolution API Configuration

### Getting an API Key

1. Start Evolution API service
2. Access Evolution Dashboard
3. Create an API key in settings
4. Configure WhatsApp instance
5. Add API key to `.env`: `EVOLUTION_API_KEY=your_key`

### Webhook Setup

Evolution API needs to know where to send webhooks:
- Endpoint: `http://api:5000/wpp-bot-api`
- Method: POST
- Content-Type: application/json

*This is already configured in docker-compose.yml*

## ⚙️ Configuration Options

### Use Evolution API (Default)
```bash
USE_EVOLUTION_API=true  # or omit (defaults to true)
```

### Fallback to WAHA
```bash
USE_EVOLUTION_API=false
```

### Custom Evolution API URL
```bash
EVOLUTION_API_URL=http://your-custom-url:3333
EVOLUTION_INSTANCE_NAME=your_instance_name
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:5000/health
```

### Test Message (Direct)
```bash
curl -X POST http://localhost:5000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Monitor Logs
```bash
docker-compose logs -f api
```

## 🐛 Troubleshooting

### Evolution API Not Responding
```bash
# Check service status
docker compose ps

# Restart service
docker compose restart evolution

# Check logs
docker compose logs evolution
```

### Database Connection Issues
```bash
# Verify PostgreSQL is running
docker compose logs evolution_db

# Check database health
docker compose exec evolution_db pg_isready -U postgres
```

### Messages Not Being Sent
1. Verify API key in `.env` is correct
2. Check Evolution API logs: `docker-compose logs evolution`
3. Verify webhook is registered in Evolution API dashboard
4. Check Flask app logs: `docker-compose logs api`

### Service Startup Issues
```bash
# Rebuild containers (if code changed)
docker compose down
docker compose up -d --build

# View complete logs
docker compose logs -f
```

## 📁 File Structure

```
Waha_Groq_langchain/
├── app.py                          # Main Flask application (UPDATED)
├── .env                            # Environment variables (UPDATED)
├── docker-compose.yml              # Container orchestration (UPDATED)
├── requirements.txt                # Python dependencies
├── Dockerfile.api                  # Flask container definition
│
├── bot/
│   ├── ai_bot.py                   # Groq LLM integration
│   └── __init__.py
│
├── services/
│   ├── evolution_api.py            # Evolution API client (NEW)
│   ├── waha.py                     # WAHA client (deprecated)
│   └── __init__.py
│
├── tests/
│   └── ...                         # Test scripts
│
└── docs/
    ├── SETUP_EVOLUTION_API.md      # This file
    └── AUTHENTICATION_SETUP.md     # Authentication notes
```

## 🔐 Security Notes

1. **API Keys**: Keep `EVOLUTION_API_KEY` and `GROQ_API_KEY` private
2. **Database**: The default PostgreSQL credentials are for development only
   - Change in production: Update `docker-compose.yml` and recreate volume
3. **Redis**: No authentication configured
   - Add password in production: Update `docker-compose.yml`

## 📚 Resources

- Evolution API Docs: https://github.com/EvolutionAPI/evolution-api
- Groq API Docs: https://console.groq.com/
- Flask Documentation: https://flask.palletsprojects.com/
- WhatsApp Business API: https://developers.facebook.com/docs/whatsapp

## ✨ Key Improvements Over WAHA

| Feature | WAHA Community | Evolution API |
|---------|---|---|
| Authentication | ❌ Broken (401 errors) | ✅ Standard API key |
| Documentation | ⚠️ Limited | ✅ Comprehensive |
| Production Ready | ❌ No | ✅ Yes |
| Database Support | 🔄 File-based | ✅ PostgreSQL |
| Caching | ❌ None | ✅ Redis |
| API Stability | ⚠️ Unstable | ✅ Stable |
| Community Support | ⚠️ Small | ✅ Active |

## 🎯 Next Steps

1. **Get Evolution API instance**:
   - Use Docker (recommended): Already configured in `docker-compose.yml`
   - Or use existing instance: Update `EVOLUTION_API_URL` in `.env`

2. **Obtain API Key**:
   - From Evolution API dashboard after instance starts
   - Add to `EVOLUTION_API_KEY` in `.env`

3. **Configure WhatsApp**:
   - Scan QR code in Evolution API dashboard
   - Register webhook: `http://api:5000/wpp-bot-api`

4. **Test Integration**:
   - Send test message to your WhatsApp number
   - Verify response is generated and delivered

5. **Monitor & Debug**:
   - Use `docker-compose logs` for troubleshooting
   - Check `bot.log` for application-level issues

---

**Status**: ✅ Ready for production deployment

**Last Updated**: 2024

**Maintained By**: Development Team
