# 🚀 Guia Rápido - Bot WhatsApp

## Iniciar Sistema
```bash
cd /home/andre-souza/Desktop/Vscode/bot_wtas/Waha_Groq_langchain
sudo docker compose up -d
```

## Acessar Dashboard
🌐 http://localhost:5000

## Como Usar

### 📱 Receber Mensagens
1. Cliente envia mensagem pelo WhatsApp
2. IA gera resposta automaticamente
3. Resposta aparece na aba "Mensagens" do dashboard

### 📋 Copiar e Enviar Resposta
1. Abrir dashboard → Aba "Mensagens"
2. Clicar na mensagem desejada
3. Clicar em "📋 Copiar Resposta"
4. Colar e enviar manualmente pelo WhatsApp

### ⏰ Criar Lembrete
1. Abrir dashboard → Aba "Lembretes"
2. Clicar em "➕ Novo Lembrete"
3. Preencher:
   - Número (ex: 554792435128)
   - Mensagem do lembrete
   - Data (YYYY-MM-DD)
   - Hora (HH:MM)
   - Recorrente: nao/diario/semanal
4. Clicar em "Salvar"
5. Scheduler tentará enviar no horário agendado

**⚠️ Nota**: Envio automático não funciona na versão Community do WAHA. O lembrete será detectado mas você precisará copiar e enviar manualmente.

## Verificar Status

### Container rodando?
```bash
sudo docker compose ps
```
Deve mostrar:
- `waha` → Running
- `api` → Running

### API funcionando?
```bash
curl http://localhost:5000/health
```
Deve retornar: `{"status": "ok"}`

### Scheduler ativo?
```bash
sudo docker compose logs api | grep scheduler
```
Deve mostrar: `Scheduler iniciado com sucesso`

## Ver Logs
```bash
# Logs da API (webhook e processamento)
sudo docker compose logs api | tail -50

# Logs do WAHA (recebimento de mensagens)
sudo docker compose logs waha | tail -50

# Logs do scheduler (lembretes)
sudo docker compose logs api | grep -i reminder
```

## Testar Sistema

### 1. Enviar Mensagem de Teste
- Envie "oi" pelo WhatsApp para o número conectado
- Aguarde 2-3 segundos
- Verifique dashboard → Aba Mensagens
- Deve aparecer mensagem + resposta da IA

### 2. Criar Lembrete de Teste
```bash
curl -X POST http://localhost:5000/api/reminders \
  -H "Content-Type: application/json" \
  -d '{
    "numero": "554792435128",
    "mensagem": "Teste do sistema!",
    "data": "2026-01-20",
    "hora": "01:50",
    "recorrente": "nao",
    "ativo": true
  }'
```

### 3. Verificar Lembrete Criado
- Abrir dashboard → Aba Lembretes
- Deve aparecer na lista
- Status: "Ativo"

## Comandos de Manutenção

### Reiniciar API
```bash
sudo docker compose restart api
```

### Reiniciar WAHA
```bash
sudo docker compose restart waha
```

### Reconstruir API (após mudanças no código)
```bash
sudo docker compose up -d --build api
```

### Parar Tudo
```bash
sudo docker compose down
```

### Limpar Volumes (⚠️ Apaga dados!)
```bash
sudo docker compose down -v
```

## Problemas Comuns

### Dashboard não carrega
✅ Verificar se API está rodando: `sudo docker compose ps`
✅ Verificar logs: `sudo docker compose logs api | tail -20`
✅ Tentar acessar: http://localhost:5000/health

### Mensagens não aparecem
✅ Verificar WAHA conectado: `curl http://localhost:3000/api/sessions/default`
✅ Verificar webhook configurado no WAHA
✅ Ver logs: `sudo docker compose logs api | grep webhook`

### Scheduler não envia lembretes
⚠️ **Normal!** WAHA Community não tem endpoint de envio
✅ Verificar se scheduler está rodando: `logs api | grep scheduler`
✅ Lembrete aparece no dashboard para copiar manualmente

### WAHA desconectado
```bash
# Reiniciar WAHA
sudo docker compose restart waha

# Aguardar 30 segundos
sleep 30

# Verificar novamente
curl http://localhost:3000/api/sessions/default
```

## Arquivos Importantes

```
messages.json       → Database de mensagens recebidas
lembretes.json      → Database de lembretes agendados
.env                → Credenciais e configurações
docker-compose.yml  → Orquestração dos containers
app.py              → API Flask principal
```

## Endpoints Úteis

```bash
# Health check
GET http://localhost:5000/health

# Listar mensagens
GET http://localhost:5000/api/messages

# Listar lembretes
GET http://localhost:5000/api/reminders

# Estatísticas de mensagens
GET http://localhost:5000/api/stats

# Estatísticas de lembretes
GET http://localhost:5000/api/reminders/stats
```

## 🎯 Workflow Diário

1. **Manhã**: Iniciar sistema
   ```bash
   cd ~/Desktop/Vscode/bot_wtas/Waha_Groq_langchain
   sudo docker compose up -d
   ```

2. **Durante o dia**: Monitorar dashboard
   - Abrir http://localhost:5000
   - Verificar aba "Mensagens" para novas mensagens
   - Copiar respostas e enviar manualmente
   - Verificar aba "Lembretes" para lembretes pendentes

3. **Noite**: Revisar logs
   ```bash
   sudo docker compose logs api | grep -E "ERROR|WARNING"
   ```

4. **Opcional**: Parar sistema
   ```bash
   sudo docker compose down
   ```

---

📚 **Documentação completa**: Ver arquivo `SISTEMA_COMPLETO.md`
