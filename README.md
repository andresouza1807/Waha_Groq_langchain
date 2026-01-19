# 🤖 WhatsApp Bot com Groq LLM e Evolution API

Bot inteligente para WhatsApp que utiliza **Groq LLM** (Llama 3.3 70B) para gerar respostas em tempo real e **Evolution API** para integração com WhatsApp.

## 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Python 3.10+** (para desenvolvimento local)
- **Groq API Key** - [Obter aqui](https://console.groq.com)
- **Evolution API** - [Documentação](https://doc.evolution-api.com)
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

# Evolution API (configure sua instância Evolution API)
EVOLUTION_API_URL=http://evolution:3333
EVOLUTION_API_KEY=sua_evolution_api_key
EVOLUTION_INSTANCE_NAME=default
```

### 3️⃣ Iniciar os Containers

```bash
docker-compose up -d
### 3️⃣ Iniciar os Containers

```bash
sudo docker compose up -d --build
```

Aguarde 30-60 segundos para os serviços iniciarem.

### 4️⃣ Verificar Status

```bash
# Ver logs da API
docker compose logs -f api

# Ver status dos containers
docker compose ps

# Testar endpoint de saúde
curl http://localhost:5000/health
```

## 🔧 Configuração da Evolution API

A Evolution API deve ser configurada separadamente. Consulte [SETUP_EVOLUTION_API.md](SETUP_EVOLUTION_API.md) para instruções detalhadas.

### Configurar Webhook

Configure o webhook na Evolution API apontando para:
```
http://api:5000/wpp-bot-api
```

## 📡 Testando o Bot

### Via cURL (Teste Direto)

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

## 🔍 Troubleshooting

### Script de Diagnóstico

```bash
python diagnose_bot.py
```

Isso verifica:
- ✓ Variáveis de ambiente
- ✓ Conexão com Groq
- ✓ Conexão com Evolution API
- ✓ Inicialização do bot
- ✓ Logs recentes

### Verificar Logs

```bash
# Ver logs da API
docker compose logs -f api

# Ver logs específicos
docker compose logs api | grep "ERROR"
docker compose logs api | grep "Message sent"
```

### Problemas Comuns

#### ❌ Erro de autenticação Groq

**Problema:** Bot retorna erro 401 ao tentar usar Groq LLM

**Solução:**
1. Verifique `GROQ_API_KEY` no `.env`
2. Copie a chave corretamente sem espaços
3. **Importante:** Rebuild dos containers: `docker compose down && docker compose up -d --build`
   - Apenas `restart` não recarrega variáveis do .env
   - Use `--build` para aplicar mudanças no .env

#### ❌ Bot não responde mensagens

**Verificar:**
1. GROQ_API_KEY está configurada? → `docker compose exec api env | grep GROQ`
2. Webhook foi configurado na Evolution API?
3. Instância WhatsApp está conectada?

#### ❌ Connection refused - Evolution API

**Problema:** Não consegue conectar à Evolution API

**Solução:**
```bash
# Verificar se containers estão rodando
docker compose ps

# Verificar logs
docker compose logs -f api

# Restart dos containers
docker compose restart
```

## 📁 Estrutura do Projeto

```
Waha_Groq_langchain/
├── app.py                      # Aplicação Flask principal
├── bot/
│   ├── __init__.py
│   └── ai_bot.py              # Lógica da IA com Groq
├── services/
│   ├── __init__.py
│   └── evolution_api.py       # Cliente Evolution API
├── docker-compose.yml         # Orquestração de containers
├── Dockerfile.api             # Imagem Docker da API
├── requirements.txt           # Dependências Python
├── .env                       # Variáveis de ambiente
├── tests/
│   └── diagnose_bot.py        # Script de diagnóstico
└── README.md                  # Este arquivo
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
Evolution API
```
POST /wpp-bot-api
```

Recebe eventos da Evolution API e processa mensagens do WhatsApp.

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

### Rodar Localmente

```bash
# Iniciar apenas PostgreSQL e Redis
docker compose up -d evolution_db evolution_redis

# Rodar API localmente
python app.py
```

## 📊 Monitoramento

### Ver Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# Apenas API
docker-compose logs -f api

```bash
# Logs da API Flask
docker compose logs -f api

# Logs do PostgreSQL
docker compose logs -f evolution_db

# Logs do Redis
docker compose logs -f evolution_redis
```

### Logs Importantes

- `✓ GROQ_API_KEY loaded successfully` - IA pronta
- `✓ WhatsApp Bot initialized with Evolution API` - Serviço iniciado
- `Processing message from` - Mensagem recebida
- `Bot response received` - IA respondeu
- `Message sent successfully` - Mensagem entregue

## 🔐 Segurança

- **GROQ_API_KEY** - Nunca compartilhe, use variáveis de ambiente
- **EVOLUTION_API_KEY** - Mantenha privada, use `.env`
- **Logs** - Contêm dados sensíveis, não compartilhe publicamente
- **Docker** - Use secrets se em produção
- **PostgreSQL** - Altere credenciais padrão em produção

## 📦 Dependências Principais

- **Flask** - Framework web
- **LangChain** - Orquestração de IA
- **Groq** - API de LLM (llama-3.3-70b-versatile)
- **Requests** - Cliente HTTP
- **PostgreSQL** - Banco de dados
- **Redis** - Cache

## 🚨 Troubleshooting Avançado

### Erro: `cannot import name 'config' from 'decouple'`

```bash
pip uninstall decouple -y
pip install python-decouple
```

### Erro: `Connection refused` - Evolution API

```bash
# Verificar se Evolution API está rodando
curl http://localhost:3333/health

# Verificar configuração
docker compose exec api env | grep EVOLUTION
```

### Bot responde com erro de autenticação

**Importante:** Mudanças no `.env` requerem rebuild:
```bash
docker compose down
docker compose up -d --build
```

## 📚 Documentação Adicional

- [SETUP_EVOLUTION_API.md](SETUP_EVOLUTION_API.md) - Guia completo Evolution API
- [README_PRODUCTION.md](README_PRODUCTION.md) - Deploy em produção
- [CHANGELOG.md](CHANGELOG.md) - Histórico de versões

## 📞 Suporte

Para problemas:

1. Verifique os logs: `docker compose logs api`
2. Execute o diagnóstico: `python tests/diagnose_bot.py`
3. Consulte [SETUP_EVOLUTION_API.md](SETUP_EVOLUTION_API.md)
4. Abra uma issue no GitHub

## 📝 Licença

MIT License - Veja LICENSE para detalhes

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

**Desenvolvido com ❤️ usando Groq LLM e Evolution API**
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
