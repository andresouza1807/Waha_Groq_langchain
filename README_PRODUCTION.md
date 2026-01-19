# WhatsApp Bot with Evolution API & Groq LLM

A production-ready WhatsApp bot powered by **Evolution API** for messaging and **Groq LLM** for AI responses.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Groq API Key: https://console.groq.com/keys
- Evolution API instance

### Installation

```bash
# 1. Clone repository
git clone https://github.com/andresouza1807/Waha_Groq_langchain.git
cd Waha_Groq_langchain

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start containers
docker compose up -d

# 4. Verify services
docker compose ps
```

## 📋 Configuration

### .env Variables

```env
# Groq LLM - Get from https://console.groq.com/keys
GROQ_API_KEY=gsk_your_key_here

# Evolution API
EVOLUTION_API_URL=http://evolution:3333
EVOLUTION_API_KEY=sk_test_your_key_here
EVOLUTION_INSTANCE_NAME=default
```

## 🏗️ Architecture

```
WhatsApp Message
    ↓
Evolution API Webhook
    ↓
Flask API (/wpp-bot-api)
    ↓
Groq LLM (llama-3.3-70b-versatile)
    ↓
Evolution API sends response back to WhatsApp
```

## 📁 Project Structure

```
.
├── app.py                      # Flask webhook & bot orchestration
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Container configuration
├── Dockerfile.api              # Flask container definition
│
├── bot/
│   └── ai_bot.py              # Groq LLM integration
│
├── services/
│   └── evolution_api.py        # Evolution API client
│
├── tests/
│   ├── test_integration.py     # Integration tests
│   └── diagnose_bot.py         # Debugging utilities
│
├── .env.example                # Environment template
├── SETUP_EVOLUTION_API.md      # Detailed setup guide
└── README.md                   # This file
```

## 🔧 Services & Ports

| Service | Port | Purpose |
|---------|------|---------|
| Evolution API | 3333 | WhatsApp messaging |
| PostgreSQL | (internal) | Evolution database |
| Redis | (internal) | Cache layer |
| Flask API | 5000 | Webhook receiver |

## 🔌 API Endpoints

### Health Check
```bash
GET /health
# Returns: {"status": "ok", "timestamp": "...", "service": "WhatsApp Bot API"}
```

### Webhook Receiver
```bash
POST /wpp-bot-api
# Evolution API sends messages here
```

### Test Endpoint
```bash
POST /test
{
  "message": "Hello, how are you?"
}
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:5000/health

# View logs
docker compose logs -f api

# Test message directly
curl -X POST http://localhost:5000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# Monitor services
docker compose ps
docker compose stats
```

## 📊 Evolution API Setup

1. **Start Evolution API**:
   - Docker will start automatically with `docker compose up`

2. **Access Dashboard**:
   - URL: `http://localhost:3333`
   - Login with default credentials

3. **Configure WhatsApp**:
   - Create instance
   - Scan QR code to connect your WhatsApp

4. **Register Webhook**:
   - Set webhook URL: `http://api:5000/wpp-bot-api`
   - Webhook should receive all message events

5. **Get API Key**:
   - Generate in Evolution dashboard
   - Add to `.env`: `EVOLUTION_API_KEY=sk_...`

## 🐛 Troubleshooting

### Services not starting
```bash
# Check logs
docker compose logs

# Rebuild
docker compose down
docker compose up -d --build
```

### Messages not being sent
1. Verify `EVOLUTION_API_KEY` is correct
2. Check Evolution API is healthy: `docker compose logs evolution`
3. Verify webhook is registered in Evolution dashboard
4. Check Flask app logs: `docker compose logs api`

### Database connection issues
```bash
# Check PostgreSQL health
docker compose exec evolution_db pg_isready -U postgres

# View Evolution logs
docker compose logs evolution
```

## 🔐 Security

- **API Keys**: Never commit `.env` to version control
- **Database**: Change default PostgreSQL credentials in production
- **Redis**: Add password authentication in production
- **HTTPS**: Use reverse proxy (nginx) in production

## 📚 Groq LLM Model

- **Model**: `llama-3.3-70b-versatile`
- **Temperature**: 0.7
- **Max Tokens**: 1024
- **Docs**: https://console.groq.com/docs/models

## 🚀 Deployment

### Docker Compose (Development)
```bash
docker compose up -d
```

### Production Checklist
- [ ] Change PostgreSQL credentials
- [ ] Set up Redis authentication
- [ ] Configure HTTPS with reverse proxy
- [ ] Use secrets management (Docker secrets or env vars)
- [ ] Set up monitoring and alerting
- [ ] Configure backups for database
- [ ] Use production Groq plan
- [ ] Test with real WhatsApp numbers

## 📝 Logs

- **Application**: `bot.log` (created in container)
- **Docker Compose**: `docker compose logs -f`
- **Specific service**: `docker compose logs -f api`

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- **Evolution API Docs**: https://github.com/EvolutionAPI/evolution-api
- **Groq API Docs**: https://console.groq.com/docs
- **Flask Docs**: https://flask.palletsprojects.com/
- **Docker Docs**: https://docs.docker.com/

## 📊 Performance

- **Message Processing**: < 2 seconds
- **AI Response Generation**: 1-5 seconds (depends on message length)
- **Database**: PostgreSQL with Redis caching
- **Scalability**: Horizontally scalable with load balancer

## ✨ Features

- ✅ Real-time WhatsApp messaging
- ✅ AI-powered responses (Groq LLM)
- ✅ Typing indicators
- ✅ Error handling & logging
- ✅ Health checks
- ✅ Docker containerization
- ✅ Database persistence
- ✅ Production-ready

## 🎯 Roadmap

- [ ] Message history/context
- [ ] Custom AI models
- [ ] Rate limiting
- [ ] User authentication
- [ ] Admin dashboard
- [ ] Analytics & metrics
- [ ] Multi-instance support

---

**Last Updated**: January 2026  
**Status**: ✅ Production Ready
