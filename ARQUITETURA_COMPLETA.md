# 🏗️ Arquitetura Completa do Sistema CRM

## 📋 Visão Geral

Sistema completo de CRM com frontend moderno, APIs REST, LLM integrado e banco de dados PostgreSQL.

```
┌─────────────────────────────────────────────────────────────────┐
│                         NAVEGADOR                               │
│                    http://localhost:3000                        │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬─────────────────┐
        │               │               │                 │
        ▼               ▼               ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌─────────────┐ ┌──────────────┐
│   Supabase    │ │  API Dados    │ │ LLM Service │ │  PostgreSQL  │
│  (Auth Only)  │ │  Port: 5000   │ │ Port: 8000  │ │ cnpj_db      │
│               │ │   Flask       │ │ LangChain   │ │ 79M records  │
│  Login/OAuth  │ │   PostgreSQL  │ │  + Gemma    │ │              │
└───────────────┘ └───────────────┘ └─────────────┘ └──────────────┘
```

---

## 🎯 Componentes do Sistema

### 1. **Frontend Next.js** (Port 3000)

**Localização:** `next-app/`

**Páginas:**
- `/` - Login/Cadastro (com modo dev)
- `/dashboard` - Dashboard principal com dados
- `/chat-llm` - Chat com LLM (Gemma)
- `/configuracoes` - Tela de configurações

**Características:**
- ✅ Autenticação Supabase (ou modo dev)
- ✅ Modo desenvolvimento (bypass auth)
- ✅ Interface moderna (Tailwind CSS)
- ✅ Integração com 2 APIs (Dados + LLM)
- ✅ Gerenciamento de configurações

**Tecnologias:**
- Next.js 14
- React 18
- Tailwind CSS
- Supabase Client

---

### 2. **API de Dados** (Port 5000)

**Localização:** `api/`

**Container:** `crm-api`

**Endpoints:**
- `GET /health` - Status da API
- `POST /query` - Executar consultas SQL

**Função:**
- Conecta ao PostgreSQL
- Processa consultas simples
- Retorna dados formatados

**Tecnologias:**
- Python 3.11
- Flask + Flask-CORS
- psycopg2 (PostgreSQL)

---

### 3. **LLM Service** (Port 8000)

**Localização:** `llm-service/`

**Container:** `crm-llm`

**Endpoints:**
- `GET /health` - Status do serviço
- `POST /ask` - Pergunta em linguagem natural
- `POST /export` - Exportar dados (CSV/PDF)

**Função:**
- Recebe perguntas em português
- Gera SQL automaticamente (via Gemma)
- Executa e retorna resultados
- Exporta para CSV/PDF

**Tecnologias:**
- Python 3.11
- Flask + Flask-CORS
- LangChain
- Ollama (Gemma LLM)
- SQLAlchemy
- Pandas, ReportLab

**Fluxo:**
```
Pergunta → Gemma → SQL → PostgreSQL → Resposta
```

---

### 4. **Banco de Dados PostgreSQL**

**Container:** `cnpj_postgres_final`

**Tabelas Principais:**
- `estabelecimentos` - **79.225.899 registros** ✅
- `cnaes` - 2.718 registros ✅
- `empresas` - 0 registros (em migração)
- `socios` - 0 registros (em migração)

**Colunas (estabelecimentos):**
```sql
cnpj_basico, cnpj_ordem, cnpj_dv
nome_fantasia, situacao_cadastral
cnae_fiscal_principal, municipio, uf
...
```

---

### 5. **Autenticação (Supabase)**

**Modo Produção:**
- Login com email/senha
- Cadastro de usuários
- OAuth (Google, GitHub, etc)
- JWT tokens automáticos

**Modo Desenvolvimento:**
- Bypass completo
- Acesso direto sem login
- LocalStorage fake user

**Toggle:**
```env
NEXT_PUBLIC_DEV_MODE=true  # Dev
NEXT_PUBLIC_DEV_MODE=false # Prod
```

---

## 🐳 Docker Compose

### Serviços Configurados:

```yaml
services:
  api:            # Port 5000 - API de Dados
  llm-service:    # Port 8000 - LLM (LangChain + Gemma)
  next-app:       # Port 3001 - Frontend (produção)
```

### Iniciar Serviços:

```bash
# API de Dados
docker-compose up -d api

# LLM Service (requer Ollama rodando)
docker-compose up -d llm-service

# Frontend (produção)
docker-compose up -d next-app

# Todos os serviços
docker-compose up -d
```

---

## 🚀 Fluxo de Uso

### Cenário 1: Modo Desenvolvimento (Atual)

```
1. Usuário → http://localhost:3000
2. Clica em "Entrar no Dashboard (Sem Login)"
3. Acessa Dashboard
4. Vê dados do PostgreSQL (79M estabelecimentos)
5. Clica em "🤖 Chat LLM"
6. Faz pergunta: "Mostre empresas de SP"
7. Gemma gera SQL
8. Retorna resultados
9. Exporta CSV/PDF
```

### Cenário 2: Modo Produção (Supabase)

```
1. Usuário → http://localhost:3000
2. Faz login/cadastro via Supabase
3. JWT token gerado
4. Acessa Dashboard (protegido)
5. Usa sistema normalmente
```

---

## ⚙️ Variáveis de Ambiente

### Frontend (`next-app/.env.local`):

```env
# Supabase (Autenticação)
NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua-chave-aqui

# API Local (Dados PostgreSQL)
NEXT_PUBLIC_API_URL=http://localhost:5000

# LLM Service (LangChain + Gemma)
NEXT_PUBLIC_LLM_URL=http://localhost:8000

# Modo de Desenvolvimento
NEXT_PUBLIC_DEV_MODE=true
```

### API de Dados (Docker):

```env
DB_HOST=cnpj_postgres_final
DB_PORT=5432
DB_NAME=cnpj_processed
DB_USER=postgres
DB_PASSWORD=password
USE_POSTGRES=true
```

### LLM Service (Docker):

```env
DB_HOST=cnpj_postgres_final
DB_PORT=5432
DB_NAME=cnpj_processed
DB_USER=postgres
DB_PASSWORD=password
OLLAMA_HOST=http://host.docker.internal:11434
```

---

## 📊 Estrutura de Dados

### Exemplo de Query LLM:

**Pergunta:** "Quantas empresas temos em São Paulo?"

**SQL Gerado:**
```sql
SELECT COUNT(*) as total
FROM estabelecimentos
WHERE uf = 'SP'
LIMIT 100
```

**Resposta:** "Encontrei 12.345.678 estabelecimentos no estado de São Paulo."

---

## 🔧 Como Usar

### 1. Pré-requisitos:

```bash
# Instalar Ollama
# https://ollama.ai

# Baixar modelo Gemma
ollama pull gemma:latest

# Verificar
ollama list
```

### 2. Iniciar Serviços:

```bash
# Terminal 1: Frontend
cd next-app
npm install
npm run dev

# Terminal 2: API de Dados
docker-compose up -d api

# Terminal 3: LLM Service
docker-compose up -d llm-service
```

### 3. Acessar:

- **Frontend:** http://localhost:3000
- **API Dados:** http://localhost:5000/health
- **LLM Service:** http://localhost:8000/health

---

## 📁 Estrutura de Arquivos

```
CRM/
├── next-app/                    # Frontend Next.js
│   ├── pages/
│   │   ├── index.jsx           # Login
│   │   ├── dashboard.jsx       # Dashboard
│   │   ├── chat-llm.jsx        # Chat LLM
│   │   └── configuracoes.jsx   # Configurações
│   ├── components/
│   │   ├── AuthForm.jsx        # Formulário auth
│   │   └── DataTable.jsx       # Tabela de dados
│   └── lib/
│       ├── supabaseClient.js   # Cliente Supabase
│       └── apiClient.js        # Cliente API
│
├── api/                         # API de Dados
│   ├── app.py                  # Flask API
│   ├── Dockerfile
│   └── requirements.txt
│
├── llm-service/                 # LLM Service
│   ├── llm_api.py              # Flask + LangChain
│   ├── Dockerfile
│   └── requirements.txt
│
└── docker-compose.yml           # Orquestração
```

---

## 🎯 Funcionalidades

### ✅ Implementadas:

- [x] Autenticação Supabase completa
- [x] Modo de desenvolvimento (bypass)
- [x] API de dados PostgreSQL
- [x] LLM Service (LangChain + Gemma)
- [x] Chat com IA em linguagem natural
- [x] Exportação CSV/PDF
- [x] Dashboard com dados reais
- [x] Tela de configurações
- [x] Containerização completa

### 🔄 Em Desenvolvimento:

- [ ] Migração completa de dados para PostgreSQL
- [ ] Autenticação OAuth (Google, GitHub)
- [ ] Sistema de permissões
- [ ] Gráficos e métricas

---

## 🐛 Troubleshooting

### LLM Service não conecta:

```bash
# Verificar Ollama
ollama list

# Testar
curl http://localhost:11434/api/tags

# Iniciar Ollama
ollama serve
```

### API não retorna dados:

```bash
# Verificar tabela
docker exec cnpj_postgres_final psql -U postgres -d cnpj_processed -c "SELECT COUNT(*) FROM estabelecimentos;"

# Ver logs
docker logs crm-api
docker logs crm-llm
```

### Frontend não carrega:

```bash
# Reiniciar
cd next-app
npm run dev

# Limpar cache
rm -rf .next
npm run dev
```

---

## 🔒 Segurança

### Modo Desenvolvimento:
- ⚠️ Apenas para testes locais
- ⚠️ Sem autenticação real
- ⚠️ NUNCA usar em produção

### Modo Produção:
- ✅ Autenticação Supabase
- ✅ JWT tokens
- ✅ RLS (Row Level Security)
- ✅ CORS configurado
- ✅ Variáveis de ambiente

---

## 📞 Suporte

### Documentação:
- `README.md` - Visão geral
- `MODO_DEV.md` - Modo desenvolvimento
- `INTEGRACAO_API.md` - Detalhes da API
- `SETUP_GOOGLE_AUTH.md` - OAuth Google
- `ARQUITETURA_COMPLETA.md` - Este arquivo

### Logs:
```bash
# API
docker logs crm-api --tail 50

# LLM
docker logs crm-llm --tail 50

# Frontend
# Ver terminal onde rodou npm run dev
```

---

## 🎉 Status Final

```
┌─────────────────────────────────────────┐
│  ✅ SISTEMA COMPLETO E ORGANIZADO       │
├─────────────────────────────────────────┤
│  Frontend:  ✅ Rodando (Port 3000)      │
│  API Dados: ✅ Rodando (Port 5000)      │
│  LLM Service: ⏳ Pronto (Port 8000)     │
│  PostgreSQL: ✅ 79M registros           │
│  Supabase:  🟡 Config manual            │
├─────────────────────────────────────────┤
│  🎯 SEM PONTAS SOLTAS                   │
│  📦 TUDO CONTAINERIZADO                 │
│  🔒 BANCO INTOCADO                      │
└─────────────────────────────────────────┘
```

---

**Criado em:** 13/10/2025  
**Versão:** 2.0.0  
**Stack:** Next.js + Flask + LangChain + Gemma + PostgreSQL + Supabase

