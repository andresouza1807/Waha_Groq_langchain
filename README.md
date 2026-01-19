# 🤖 WhatsApp Bot com Groq LLM e Waha

Bot inteligente para WhatsApp que utiliza **Groq LLM** (Llama 3.3 70B) para gerar respostas em tempo real e **Waha API** para integração com WhatsApp.

## 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Python 3.10+** (para desenvolvimento local)
- **Groq API Key** - [Obter aqui](https://console.groq.com)
- **Waha API Key** - [Obter aqui](https://waha.devlikeapro.com)
- **WhatsApp** para testar o bot

## 🚀 Início Rápido

### 1️⃣ Clonar o Repositório

```bash
git clone https://github.com/andresouza1807/Waha_Groq_langchain.git
cd Waha_Groq_langchain
```

### 2️⃣ Configurar Variáveis de Ambiente

Crie/edite o arquivo `.env` com suas chaves:

```bash
# Groq API (obtenha em https://console.groq.com)
GROQ_API_KEY=gsk_seu_api_key_aqui

# Waha API (obtenha em https://waha.devlikeapro.com)
WAHA_API_KEY=sua_waha_api_key
WAHA_URL=http://wpp_bot_waha:3000
WAHA_SESSION_NAME=default

# Dashboard Waha (credenciais opcionais)
WAHA_DASHBOARD_USERNAME=admin
WAHA_DASHBOARD_PASSWORD=sua_senha
```

### 3️⃣ Iniciar os Containers

```bash
docker-compose up -d
```

Aguarde 30-60 segundos para WAHA e API iniciarem.

### 4️⃣ Verificar Status

```bash
# Ver logs da API
docker-compose logs -f api

# Ver logs do WAHA
docker-compose logs -f waha

# Listar containers
docker-compose ps
```

## 🔧 Configuração do Waha

### Acessar o Dashboard

Abra seu navegador e vá para: `http://localhost:3000/dashboard`

### Configurar Webhook

1. Na aba **Sessions**, clique em **Configuration**
2. Configure o webhook com a URL:
   ```
   http://api:5000/wpp-bot-api
   ```
3. Em **Events**, selecione apenas **Message**
4. Clique em **Update**

### Iniciar Sessão WhatsApp

1. Na aba **Sessions**, clique em **Start**
2. Quando aparecer "Login", clique no botão **Login**
3. Escaneie o QR code com seu WhatsApp
4. Aguarde a sincronização (o status mudará para "CONNECTED")

## 📡 Testando o Bot

### Via cURL (Teste de Webhook)

```bash
curl -X POST http://localhost:5000/test \
  -H "Content-Type: application/json" \
  -d '{"message":"Olá! Como você está?"}'
```

Resposta esperada:
```json
{
  "input": "Olá! Como você está?",
  "response": "Estou bem, obrigado! Como posso ajudar?",
  "status": "success"
}
```

### Via WhatsApp

Envie qualquer mensagem para o número vinculado. O bot responderá com:
- Indicador de digitação ("digitando...")
- Resposta gerada pela Groq IA
- Sem erros nos logs

## 🔍 Diagnosticar Problemas

### Script de Diagnóstico

```bash
python diagnose_bot.py
```

Isso verifica:
- ✓ Variáveis de ambiente
- ✓ Conexão com Groq
- ✓ Conexão com Waha
- ✓ Inicialização do bot
- ✓ Logs recentes

### Verificar Logs

```bash
# Ver últimas linhas do bot.log
tail -f bot.log

# Ver logs específicos
grep "ERROR" bot.log
grep "Message sent" bot.log
```

### Problemas Comuns

#### ❌ 401 Unauthorized do Waha

**Problema:** Bot recebe erro 401 ao tentar se conectar ao Waha

**Solução:**
1. Verifique `WAHA_API_KEY` no `.env`
2. Copie a chave corretamente sem espaços
3. Reinicie os containers: `docker-compose restart`

#### ❌ Bot não responde mensagens

**Verificar:**
1. GROQ_API_KEY está configurada? → `docker-compose logs api | grep GROQ`
2. Webhook foi configurado? → Verificar no dashboard do Waha
3. Status da sessão é CONNECTED? → Ver no dashboard

#### ❌ Connection refused - Waha

**Problema:** Não consegue conectar ao `wpp_bot_waha:3000`

**Solução:**
```bash
# Verificar se containers estão rodando
docker-compose ps

# Reiniciar Waha
docker-compose restart waha

# Aguardar inicialização (30-60s)
sleep 30
```

## 📁 Estrutura do Projeto

```
Waha_Groq_langchain/
├── app.py                 # Aplicação Flask principal
├── bot/
│   ├── __init__.py
│   └── ai_bot.py         # Lógica da IA com Groq
├── services/
│   ├── __init__.py
│   └── waha.py           # Cliente API do Waha
├── docker-compose.yml    # Orquestração de containers
├── Dockerfile.api        # Imagem Docker da API
├── requirements.txt      # Dependências Python
├── .env                  # Variáveis de ambiente
├── diagnose_bot.py       # Script de diagnóstico
└── README.md            # Este arquivo
```

## 🔌 API Endpoints

### Health Check
```
GET /health
```

Resposta:
```json
{
  "status": "ok",
  "timestamp": "2026-01-18T00:00:00",
  "service": "WhatsApp Bot API"
}
```

### Webhook Waha
```
POST /wpp-bot-api
```

Payload esperado:
```json
{
  "payload": {
    "type": "chat",
    "from": "5511999999999",
    "body": "Sua mensagem"
  }
}
```

### Endpoint de Teste
```
POST /test
```

Payload:
```json
{
  "message": "Sua mensagem aqui"
}
```

## 🛠️ Desenvolvimento Local

### Instalar Dependências

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Rodar Sem Docker

```bash
# Terminal 1: Iniciar Waha (via Docker)
docker run -p 3000:3000 devlikeapro/waha:latest

# Terminal 2: Rodar API local
python app.py
```

## 📊 Monitoramento

### Ver Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# Apenas API
docker-compose logs -f api

# Apenas Waha
docker-compose logs -f waha
```

### Logs Importantes

- `✓ GROQ_API_KEY loaded successfully` - IA pronta
- `✓ Authorization header will be sent` - Waha autenticado
- `Processing message from` - Mensagem recebida
- `Bot response received` - IA respondeu
- `Message sent successfully` - Mensagem entregue

## 🔐 Segurança

- **GROQ_API_KEY** - Nunca compartilhe, use variáveis de ambiente
- **WAHA_API_KEY** - Mantenha privada, use `.env`
- **Logs** - Contêm dados sensíveis, não compartilhe publicamente
- **Docker** - Use secrets se em produção

## 📦 Dependências Principais

- **Flask** - Framework web
- **LangChain** - Orquestração de IA
- **Groq** - API de LLM
- **Requests** - Cliente HTTP

## 🚨 Troubleshooting

### Erro: `cannot import name 'config' from 'decouple'`

```bash
pip uninstall decouple -y
pip install python-decouple
```

### Erro: `Connection refused` do Waha

```bash
# Aguardar inicialização do Waha
sleep 60
docker-compose logs waha | tail -10
```

### Bot responde com vazio

1. Verifique `GROQ_API_KEY`
2. Teste com `curl -X POST http://localhost:5000/test -H "Content-Type: application/json" -d '{"message":"teste"}'`
3. Veja logs: `tail -f bot.log`

## 📞 Suporte

Para problemas:

1. Verifique os logs: `docker-compose logs api`
2. Execute diagnóstico: `python diagnose_bot.py`
3. Consulte documentação:
   - [Waha Docs](https://waha.devlikeapro.com)
   - [Groq Docs](https://console.groq.com/docs)

## 📜 Licença

Projeto aberto para uso educacional e comercial.

## 👨‍💻 Autor

André Souza - [GitHub](https://github.com/andresouza1807)

---

**Última atualização:** Janeiro 2026  
**Versão:** 2.0 

---
