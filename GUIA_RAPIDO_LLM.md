# 🚀 Guia Rápido - Chat LLM (Gemma)

## 📋 O Que Foi Implementado

Transformei seu script `Langchain gemma BDsqlite.py` em um **serviço web containerizado** totalmente integrado ao CRM!

### Antes (Script):
```python
# CLI com tkinter
# SQLite local
# Execução manual
python "Langchain gemma BDsqlite.py"
```

### Agora (Container + Web):
```
🌐 Interface web moderna
🐳 Container Docker
🗄️ PostgreSQL (79M registros)
🤖 Chat com IA em tempo real
📊 Exportação CSV/PDF integrada
```

---

## 🎯 Como Usar

### 1. **Pré-requisito: Instalar Ollama**

#### Windows:
1. Baixe: https://ollama.ai/download
2. Instale o executável
3. Abra PowerShell e execute:
```powershell
ollama pull gemma:latest
```

#### Verificar instalação:
```powershell
ollama list
# Deve mostrar: gemma:latest
```

---

### 2. **Iniciar o Serviço LLM**

```powershell
# No diretório do projeto
cd C:\Users\PwC\Documents\CRM

# Iniciar container
docker-compose up -d llm-service

# Verificar logs
docker logs crm-llm

# Deve mostrar:
# ✅ LangChain + Gemma inicializado com sucesso!
```

---

### 3. **Acessar o Chat**

1. **Abra:** http://localhost:3000
2. **Entre no Dashboard** (modo dev ou login)
3. **Clique em:** 🤖 **Chat LLM**

---

## 💬 Exemplos de Uso

### Perguntas que Funcionam:

```
"Quantos estabelecimentos temos?"
→ SQL: SELECT COUNT(*) FROM estabelecimentos
→ Resposta: "Existem 79.225.899 estabelecimentos"

"Mostre 10 empresas de São Paulo"
→ SQL: SELECT * FROM estabelecimentos WHERE uf = 'SP' LIMIT 10
→ Retorna tabela com dados

"Quais são os CNAEs mais comuns?"
→ SQL: SELECT cnae_fiscal_principal, COUNT(*) ...
→ Resposta com estatísticas

"Liste empresas com situação cadastral ativa em MG"
→ SQL: SELECT * FROM estabelecimentos WHERE uf = 'MG' AND situacao_cadastral = '02'
→ Dados filtrados
```

---

## 📊 Exportar Dados

Após cada resposta com dados, você pode:

1. **Botão "📥 CSV"** - Baixa arquivo CSV
2. **Botão "📥 PDF"** - Baixa arquivo PDF

Os arquivos são gerados automaticamente!

---

## 🔍 Status do Serviço

### Verificar se está funcionando:

```powershell
# Testar API
curl.exe http://localhost:8000/health

# Resposta esperada:
{
  "status": "ok",
  "service": "LLM Service (LangChain + Gemma)",
  "ollama_connected": true,
  "database": "cnpj_processed"
}
```

---

## 🎨 Interface do Chat

```
┌──────────────────────────────────────────┐
│  🤖 Chat com LLM (Gemma)      ← Dashboard │
│  🟢 Ollama conectado                     │
├──────────────────────────────────────────┤
│                                          │
│  💬 Faça uma pergunta sobre seus dados   │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │ Você: Quantas empresas em SP?     │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │ 🤖: Existem 12.345.678 estab...   │  │
│  │ Ver SQL gerado ▼                  │  │
│  │ 📊 12345678 resultados            │  │
│  │ [📥 CSV] [📥 PDF]                 │  │
│  └────────────────────────────────────┘  │
│                                          │
├──────────────────────────────────────────┤
│  Digite sua pergunta...        [🚀]     │
└──────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### ❌ "LLM Service offline"

**Causa:** Container não está rodando ou Ollama offline

**Solução:**
```powershell
# 1. Verificar Ollama
ollama list

# 2. Iniciar Ollama (se necessário)
ollama serve

# 3. Reiniciar container
docker-compose restart llm-service

# 4. Ver logs
docker logs crm-llm --tail 30
```

### ❌ "Ollama desconectado"

**Causa:** Ollama não está rodando

**Solução:**
```powershell
# Abrir novo terminal e executar:
ollama serve

# Deixar rodando em background
```

### ❌ Resposta lenta

**Normal!** O Gemma leva alguns segundos para:
1. Gerar o SQL (5-10 seg)
2. Executar a query (1-5 seg)
3. Formular a resposta (3-5 seg)

**Total:** 10-20 segundos por pergunta

---

## 🔧 Configurações Avançadas

### Trocar o modelo LLM:

Edite `llm-service/llm_api.py`:

```python
# Linha 48
llm = OllamaLLM(
    model="gemma:latest",  # Trocar aqui
    base_url=OLLAMA_HOST,
    temperature=0
)
```

**Modelos disponíveis:**
- `gemma:latest` - Atual (recomendado)
- `llama2` - Alternativa
- `mistral` - Mais rápido
- `codellama` - Focado em código

**Baixar novo modelo:**
```powershell
ollama pull llama2
```

---

## 📊 Comparação com o Script Antigo

| Feature | Script Antigo | Nova Versão |
|---------|--------------|-------------|
| Interface | CLI (tkinter) | Web moderna |
| Banco | SQLite | PostgreSQL |
| Deploy | Local apenas | Container Docker |
| Acesso | 1 usuário | Multi-usuário |
| Exportação | Arquivo local | Download web |
| Integração | Isolado | Integrado ao CRM |
| Status | Manual | Monitoramento web |

---

## 🎯 Fluxo Completo

```
1. Usuário faz pergunta no chat web
   ↓
2. Frontend envia para LLM Service (port 8000)
   ↓
3. LangChain processa com Gemma
   ↓
4. Gemma gera SQL otimizado
   ↓
5. SQL executado no PostgreSQL
   ↓
6. Resultados processados
   ↓
7. Gemma formula resposta em português
   ↓
8. Frontend exibe:
   - Resposta textual
   - SQL gerado
   - Botões de export
   ↓
9. Usuário pode exportar CSV/PDF
```

---

## 🔐 Segurança

### ⚠️ Importante:

O LLM Service:
- ✅ Roda apenas localmente
- ✅ Não expõe dados externamente
- ✅ Gera SQL seguro (sem DROP, DELETE, etc)
- ✅ Limita resultados (max 100 registros)

### Para Produção:

Adicione autenticação ao LLM Service:
```python
# llm-service/llm_api.py
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"erro": "Não autorizado"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/ask', methods=['POST'])
@require_auth
def ask_question():
    ...
```

---

## 📝 Logs e Debug

### Ver o que está acontecendo:

```powershell
# Logs do LLM Service
docker logs crm-llm -f

# Você verá:
# [LLM] Pergunta recebida: ...
# [SQL] Gerado: SELECT ...
# [RESULTADO] 123 registros
```

---

## 🎉 Pronto!

Agora você tem:
- ✅ Script antigo → Serviço web moderno
- ✅ SQLite → PostgreSQL (79M registros)
- ✅ CLI → Interface web bonita
- ✅ Tudo containerizado e organizado
- ✅ Sem pontas soltas!

**Próximos passos:**
1. Abra http://localhost:3000
2. Clique em "🤖 Chat LLM"
3. Faça sua primeira pergunta!

---

**Versão:** 1.0.0  
**Data:** 13/10/2025  
**Baseado em:** `Langchain gemma BDsqlite.py`

