# Solução para QR Code - Evolution API

## Problema Identificado
A Evolution API v2.2.3 está com bug no geração automática de QR Code. A instância entra em loop infinito de reconexão e nunca gera o QR.

## Soluções Alternativas

### Opção 1: Usar WAHA (Recomendado)
WAHA é mais simples e gera QR Code instantaneamente:

```bash
docker run -d \
  --name waha \
  -p 3000:3000 \
  -e WHATSAPP_API_KEY=your_secret_key \
  devlikeapro/waha
```

Acessar: http://localhost:3000/

### Opção 2: Evolution API Standalone
Execute Evolution API fora do Docker:
```bash
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api
npm install
npm run start:dev
```

### Opção 3: CodeChat (Mais Estável)
```bash
docker run -d \
  --name codechat \
  -p 8080:8080 \
  -e DATABASE_PROVIDER=local \
  codechat/api:latest
```

## Status Atual
- Flask Bot API: ✅ Funcionando (porta 5000)
- Groq AI: ✅ Funcionando
- Evolution API: ⚠️ Rodando mas não gera QR Code
- PostgreSQL: ✅ Funcionando
- Redis: ✅ Funcionando

## Próximo Passo Recomendado
Use WAHA temporariamente para testar o bot end-to-end, depois migre para Evolution API quando o bug for corrigido.
