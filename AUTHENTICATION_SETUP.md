# 🔐 Setup de Autenticação WAHA

## ⚠️ Problema Atual

O WAHA Community/CORE tier retorna **401 Unauthorized** em todos os endpoints de API (`/api/sendText`, `/api/startTyping`, etc.) mesmo sem autenticação configurada.

**Erro observado:**
```
HTTP/1.1 401 Unauthorized
{"message":"Unauthorized","statusCode":401}
```

## 🔍 Causa

O WAHA Community Edition requer **autenticação obrigatória via Dashboard Web**, mas não utiliza os formatos padrão de autenticação:
- ❌ Bearer tokens
- ❌ Basic Auth
- ❌ API Keys (a chave mostrada nos logs é apenas informacional)

## ✅ Solução

### Opção 1: Acessar WAHA Dashboard (Recomendado)

1. **Acesse o Dashboard WAHA em seu navegador:**
   - URL: `http://localhost:3000` (ou seu domínio)
   - Usuário: `admin`
   - Senha: Verifique em `WAHA_DASHBOARD_PASSWORD` no `.env`

2. **Configure a autenticação:**
   - Vá para Settings/Configurações
   - Ative/configure a autenticação da sessão
   - Salve as credenciais

3. **Teste o endpoint:**
   ```bash
   # Com as credenciais corretas do Dashboard
   curl -u admin:SEU_PASSWORD -X POST http://localhost:3000/api/sendText \
     -H "Content-Type: application/json" \
     -d '{"session":"default","chatId":"554791047403@c.us","text":"Test"}'
   ```

### Opção 2: Usar WAHA PRO (Pago)

Se você usa WAHA Pro em vez de Community:
- A autenticação Bearer Token funciona corretamente
- Use a chave gerada no Dashboard Pro
- Adicione ao `.env`: `WAHA_API_KEY=sua_chave_pro`

### Opção 3: Usar Docker com Network Isolada

Configure o WAHA para aceitar conexões internas sem autenticação:

```yaml
# docker-compose.yml
environment:
  - WAHA_DOCKER_USE_SYSTEM_DEFAULT=true
  - WHATSAPP_HOOK_URL=http://api:5000/wpp-bot-api
```

## 📝 Próximos Passos

1. **Acessar Dashboard:** http://localhost:3000
2. **Configurar credenciais corretas**
3. **Testar com curl:**
   ```bash
   curl -u admin:password -X POST http://localhost:3000/api/sendText \
     -H "Content-Type: application/json" \
     -d '{"session":"default","chatId":"554791047403@c.us","text":"Test"}'
   ```
4. **Atualizar `.env` com as credenciais funcionais**
5. **Reiniciar containers:** `docker-compose restart`

## 🔗 Referências

- [WAHA Documentação oficial](https://waha.devlikeapro.com)
- [WAHA Community Edition](https://waha.devlikeapro.com/docs/overview/editions)
- [API Authentication](https://waha.devlikeapro.com/docs/how-to/api-authentication)

---

**Status Atual:** ⏸️ Aguardando configuração correta de autenticação no Dashboard WAHA
