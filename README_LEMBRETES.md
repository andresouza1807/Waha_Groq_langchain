# Sistema de Lembretes Automáticos via WhatsApp

Sistema simples para enviar lembretes programados via WhatsApp usando Evolution API.

## 🚀 Como Usar

### 1. Adicionar Lembretes

**Modo Interativo:**
```bash
python adicionar_lembrete.py
```

Responda as perguntas:
- Número WhatsApp (com DDI): `5511999999999`
- Mensagem: `Lembrete: Reunião às 14h`
- Data: Hoje/Amanhã ou data específica
- Hora: `14:00`
- Recorrência: Único, Diário, Semanal ou Mensal

**Listar lembretes:**
```bash
python adicionar_lembrete.py listar
```

**Remover lembrete:**
```bash
python adicionar_lembrete.py remover
```

### 2. Iniciar o Sistema

```bash
python scheduler_lembretes.py
```

O sistema irá:
- ✅ Verificar lembretes a cada minuto
- ✅ Enviar mensagens no horário programado
- ✅ Reagendar lembretes recorrentes automaticamente
- ✅ Mostrar próximos lembretes ao iniciar

### 3. Editar Manualmente

Você também pode editar `lembretes.json` diretamente:

```json
{
  "id": 1,
  "ativo": true,
  "numero": "5511999999999",
  "mensagem": "Sua mensagem aqui",
  "data": "2026-01-20",
  "hora": "10:00",
  "recorrente": false
}
```

**Campos:**
- `id`: Identificador único (número)
- `ativo`: `true` ou `false` (ativar/desativar)
- `numero`: WhatsApp com DDI (apenas números)
- `mensagem`: Texto do lembrete
- `data`: Formato `AAAA-MM-DD`
- `hora`: Formato `HH:MM`
- `recorrente`: `false`, `"diario"`, `"semanal"` ou `"mensal"`

## 📋 Exemplos de Uso

**Lembrete único:**
```json
{
  "id": 1,
  "ativo": true,
  "numero": "5511999999999",
  "mensagem": "Reunião importante amanhã às 14h!",
  "data": "2026-01-20",
  "hora": "10:00",
  "recorrente": false
}
```

**Lembrete diário (remédio):**
```json
{
  "id": 2,
  "ativo": true,
  "numero": "5511988888888",
  "mensagem": "🏥 Hora de tomar seu remédio!",
  "data": "2026-01-20",
  "hora": "08:00",
  "recorrente": "diario"
}
```

**Lembrete semanal:**
```json
{
  "id": 3,
  "ativo": true,
  "numero": "5511977777777",
  "mensagem": "📅 Reunião de equipe toda segunda às 9h",
  "data": "2026-01-20",
  "hora": "08:30",
  "recorrente": "semanal"
}
```

## 🔧 Requisitos

- Python 3.8+
- Evolution API rodando (porta 8080)
- WhatsApp conectado via QR Code na Evolution API
- Bibliotecas: `schedule`, `requests`

## 🎯 Funcionalidades

✅ Lembretes únicos ou recorrentes
✅ Recorrência: diária, semanal, mensal
✅ Ativar/desativar lembretes sem deletar
✅ Múltiplos números de destino
✅ Interface simples (terminal + JSON)
✅ Logs detalhados
✅ Não precisa de banco de dados

## ⚠️ Importante

1. **Formato do número:** Use DDI + DDD + número (apenas números)
   - ✅ Correto: `5511999999999`
   - ❌ Errado: `+55 (11) 99999-9999`

2. **Evolution API deve estar conectada:** Escaneie o QR Code antes de usar

3. **Horário:** Use o formato 24h (`08:00`, `14:30`, `23:00`)

4. **Data:** Formato internacional (`2026-01-20`)

## 🚨 Troubleshooting

**Lembrete não envia:**
- Verifique se `ativo: true`
- Confirme data/hora corretas
- Teste se Evolution API está respondendo: `curl http://localhost:8080/`

**Erro de conexão:**
- Verifique se Evolution API está rodando
- Confirme WhatsApp conectado via QR Code

## 📝 Próximos Passos

Depois que o WhatsApp estiver conectado na Evolution API, basta:

1. Adicionar seus lembretes
2. Rodar `python scheduler_lembretes.py`
3. Deixar rodando em background

Para rodar em background (Linux):
```bash
nohup python scheduler_lembretes.py > lembretes.log 2>&1 &
```
