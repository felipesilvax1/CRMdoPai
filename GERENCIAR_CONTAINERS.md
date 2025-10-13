# 🐳 Guia de Gerenciamento de Containers

## 📋 Estrutura Organizada

Agora os containers estão organizados em **3 arquivos Docker Compose**:

```
docker-compose.crm.yml        ⭐ CRM apenas (API + LLM)
docker-compose.frontend.yml   🌐 Frontend (produção)
docker-compose.all.yml        🎯 Tudo junto (completo)
docker-compose.test.yml       🧪 Ambiente de testes
```

---

## 🎯 MODO RECOMENDADO (Atual)

### **Containers Gerenciados Separadamente:**

```
┌─────────────────────────────────────┐
│  INFRAESTRUTURA (Manual)            │
│  • cnpj_postgres_final  ✅          │
│  • ollama               ✅          │
│  • Supabase stack       ✅          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  CRM (Docker Compose)               │
│  • crm-api          Port 5000  ✅   │
│  • crm-llm          Port 8000  ✅   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  FRONTEND (Local - Dev)             │
│  • npm run dev      Port 3000  ✅   │
└─────────────────────────────────────┘
```

---

## 🚀 COMANDOS ORGANIZADOS

### **🎯 Gerenciar CRM (Recomendado):**

```powershell
# Iniciar apenas CRM (API + LLM)
docker-compose -f docker-compose.crm.yml up -d

# Ver logs do CRM
docker-compose -f docker-compose.crm.yml logs -f

# Parar CRM
docker-compose -f docker-compose.crm.yml down

# Status do CRM
docker-compose -f docker-compose.crm.yml ps

# Rebuild CRM
docker-compose -f docker-compose.crm.yml up -d --build
```

---

### **🌐 Gerenciar Frontend (Produção):**

```powershell
# Iniciar frontend containerizado
docker-compose -f docker-compose.frontend.yml up -d

# Ver logs
docker-compose -f docker-compose.frontend.yml logs -f

# Parar
docker-compose -f docker-compose.frontend.yml down
```

---

### **🎯 Iniciar TUDO de uma vez:**

```powershell
# Iniciar todos os serviços (exceto Supabase)
docker-compose -f docker-compose.all.yml up -d

# Ver todos os logs
docker-compose -f docker-compose.all.yml logs -f

# Parar tudo
docker-compose -f docker-compose.all.yml down
```

---

## 📊 VISUALIZAR CONTAINERS ORGANIZADOS

### **Por Stack:**

```powershell
# Ver apenas CRM
docker ps --filter "label=app=crm"

# Ver por tier
docker ps --filter "label=tier=api"
docker ps --filter "label=tier=llm"
docker ps --filter "label=tier=database"
```

---

### **Status Completo:**

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Sort-Object
```

**Resultado organizado:**
```
NAMES                    STATUS              PORTS
─────────────────────────────────────────────────────────
CRM STACK:
crm-api                  Up (healthy)        5000->5000
crm-llm                  Up                  8000->8000

INFRAESTRUTURA:
cnpj_postgres_final      Up                  5432
ollama                   Up                  11434->11434

SUPABASE (Opcional):
supabase_auth_PwC        Up (healthy)        9999
supabase_db_PwC          Up (healthy)        54322->5432
supabase_kong_PwC        Up (healthy)        54321->8000
supabase_studio_PwC      Up (healthy)        54323->3000
... outros containers Supabase
```

---

## 🔧 GERENCIAR CONTAINERS ESPECÍFICOS

### **CRM API:**
```powershell
docker logs crm-api -f              # Logs
docker restart crm-api              # Reiniciar
docker exec -it crm-api sh          # Entrar no container
```

### **LLM Service:**
```powershell
docker logs crm-llm -f              # Logs
docker restart crm-llm              # Reiniciar
```

### **PostgreSQL:**
```powershell
docker logs cnpj_postgres_final -f  # Logs
docker exec -it cnpj_postgres_final psql -U postgres -d cnpj_processed
```

### **Ollama:**
```powershell
docker logs ollama -f               # Logs
docker exec -it ollama ollama list  # Ver modelos
```

---

## 🧹 LIMPEZA E MANUTENÇÃO

### **Parar containers desnecessários:**

```powershell
# Parar Supabase (se não estiver usando)
docker stop $(docker ps -q --filter "name=supabase")

# Parar frontend containerizado (se usar local)
docker stop crm-frontend
```

---

### **Remover containers parados:**

```powershell
# Ver containers parados
docker ps -a --filter "status=exited"

# Remover todos os parados
docker container prune -f
```

---

### **Limpar imagens antigas:**

```powershell
# Ver imagens
docker images

# Remover imagens não usadas
docker image prune -a -f
```

---

## 📦 SETUP INICIAL (Fresh Start)

### **Opção 1: CRM Básico (Recomendado):**

```powershell
# 1. Garantir que infraestrutura está rodando
docker start cnpj_postgres_final
docker start ollama

# 2. Iniciar CRM
docker-compose -f docker-compose.crm.yml up -d

# 3. Iniciar Frontend (local)
cd next-app
npm run dev

# 4. Acessar
# http://localhost:3000
```

---

### **Opção 2: CRM Completo (Tudo Containerizado):**

```powershell
# 1. Iniciar tudo de uma vez
docker-compose -f docker-compose.all.yml up -d

# 2. Aguardar ~30 segundos

# 3. Acessar
# http://localhost:3001 (frontend containerizado)
```

---

## 🎯 ARQUIVOS ORGANIZADOS

```
docker-compose.yml              ❌ ANTIGO (legacy)
docker-compose.crm.yml          ✅ CRM Stack (usar este!)
docker-compose.frontend.yml     ✅ Frontend (produção)
docker-compose.all.yml          ✅ Tudo junto
docker-compose.test.yml         ✅ Testes
```

---

## 📊 PORTAS ORGANIZADAS

### **CRM Stack:**
```
5000  - crm-api      (API de Dados)
8000  - crm-llm      (LLM Service)
3000  - Frontend     (npm run dev - local)
3001  - Frontend     (Docker - produção)
```

### **Infraestrutura:**
```
5432  - PostgreSQL   (interno)
11434 - Ollama       (LLM Engine)
```

### **Supabase (Opcional):**
```
54321 - Kong         (Gateway)
54322 - Supabase DB  (PostgreSQL)
54323 - Studio       (Dashboard)
54324 - Inbucket     (Email)
54327 - Analytics
```

---

## 🔍 VERIFICAR SAÚDE DO SISTEMA

```powershell
# Health checks automáticos
docker inspect crm-api | Select-String "Health"
docker inspect crm-llm | Select-String "Health"

# Testar endpoints
curl.exe http://localhost:5000/health
curl.exe http://localhost:8000/health

# Ver recursos
docker stats --no-stream crm-api crm-llm
```

---

## 🚨 TROUBLESHOOTING

### **Container não inicia:**

```powershell
# Ver logs de erro
docker logs crm-api
docker logs crm-llm

# Rebuild forçado
docker-compose -f docker-compose.crm.yml up -d --build --force-recreate
```

### **Porta em uso:**

```powershell
# Ver o que está usando a porta 5000
netstat -ano | findstr :5000

# Matar processo
taskkill /PID <PID> /F
```

### **Limpar tudo e recomeçar:**

```powershell
# Parar tudo do CRM
docker-compose -f docker-compose.crm.yml down

# Limpar volumes (CUIDADO!)
docker-compose -f docker-compose.crm.yml down -v

# Rebuild completo
docker-compose -f docker-compose.crm.yml up -d --build
```

---

## 🎯 RECOMENDAÇÃO DE USO

### **Desenvolvimento:**
```powershell
# Infraestrutura (sempre ligada)
docker start cnpj_postgres_final ollama

# CRM Stack
docker-compose -f docker-compose.crm.yml up -d

# Frontend (local - mais rápido)
cd next-app
npm run dev
```

### **Produção:**
```powershell
# Tudo containerizado
docker-compose -f docker-compose.all.yml up -d
```

---

## 📝 SCRIPTS ÚTEIS

Criei scripts para facilitar:

### **Windows:**
```powershell
# Iniciar CRM
.\start-crm.ps1

# Parar CRM  
.\stop-crm.ps1

# Status
.\status-crm.ps1
```

### **Linux/Mac:**
```bash
# Iniciar CRM
./start-crm.sh

# Parar CRM
./stop-crm.sh

# Status
./status-crm.sh
```

---

**Criado em:** 13/10/2025  
**Versão:** 1.0  
**Status:** ✅ **ORGANIZADO**

