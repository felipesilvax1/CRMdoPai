# 🐳 Containers Organizados!

## ✅ ANTES vs DEPOIS

### **ANTES** ❌ (Zona):
```
docker-compose.yml  →  Tudo misturado
                       Difícil gerenciar
                       Sem organização
```

### **DEPOIS** ✅ (Organizado):
```
docker-compose.crm.yml       →  🎯 CRM Stack (API + LLM)
docker-compose.frontend.yml  →  🌐 Frontend (Produção)
docker-compose.all.yml       →  🎁 Tudo Junto
docker-compose.test.yml      →  🧪 Testes
docker-compose.yml           →  📌 Principal (usa crm.yml)

+ Scripts PowerShell:
  start-crm.ps1   →  🚀 Iniciar CRM
  stop-crm.ps1    →  ⏹️  Parar CRM
  status-crm.ps1  →  📊 Ver Status
```

---

## 📊 ESTRUTURA ORGANIZADA

```
┌──────────────────────────────────────────┐
│  STACK 1: INFRAESTRUTURA                 │
│  (Gerenciados manualmente)               │
├──────────────────────────────────────────┤
│  • cnpj_postgres_final  (PostgreSQL)     │
│  • ollama               (LLM Engine)     │
│  • supabase_*           (Supabase - 11)  │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  STACK 2: CRM                            │
│  docker-compose.crm.yml                  │
├──────────────────────────────────────────┤
│  • crm-api    Port 5000  (API Dados)     │
│  • crm-llm    Port 8000  (LLM Service)   │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  STACK 3: FRONTEND                       │
│  Local (Dev) ou Docker (Prod)            │
├──────────────────────────────────────────┤
│  • npm run dev  Port 3000  (Dev)         │
│  • crm-frontend Port 3001  (Prod)        │
└──────────────────────────────────────────┘
```

---

## 🚀 COMANDOS SIMPLIFICADOS

### **Gerenciar CRM (Recomendado):**

```powershell
# Iniciar
.\start-crm.ps1

# Parar
.\stop-crm.ps1

# Ver status
.\status-crm.ps1
```

### **Ou usar docker-compose direto:**

```powershell
# CRM apenas (API + LLM)
docker-compose -f docker-compose.crm.yml up -d
docker-compose -f docker-compose.crm.yml logs -f
docker-compose -f docker-compose.crm.yml down

# Tudo junto (PostgreSQL + Ollama + CRM + Frontend)
docker-compose -f docker-compose.all.yml up -d
docker-compose -f docker-compose.all.yml down

# Padrão (usa crm.yml automaticamente)
docker-compose up -d
docker-compose down
```

---

## 📋 STATUS ATUAL

Execute:
```powershell
.\status-crm.ps1
```

**Mostra:**
- 🎯 CRM Stack (2 containers)
- 🏗️ Infraestrutura (postgres, ollama)
- 🔍 Supabase (11 containers)
- 💾 Uso de CPU/Memória
- 🌐 Health checks

---

## 🧹 LIMPEZA

### **Parar apenas CRM (mantém infra):**
```powershell
.\stop-crm.ps1
# ou
docker-compose -f docker-compose.crm.yml down
```

### **Parar Supabase (se não usar):**
```powershell
docker stop $(docker ps -q --filter "name=supabase")
```

### **Parar tudo:**
```powershell
docker stop $(docker ps -q)
```

---

## 🎯 WORKFLOWS RECOMENDADOS

### **Desenvolvimento Diário:**
```powershell
# Manhã - Iniciar tudo
docker start cnpj_postgres_final ollama
.\start-crm.ps1
cd next-app && npm run dev

# Durante o dia - Ver status
.\status-crm.ps1

# Noite - Parar CRM (mantém infra)
.\stop-crm.ps1
```

### **Produção:**
```powershell
# Tudo containerizado
docker-compose -f docker-compose.all.yml up -d
```

---

## 📊 VANTAGENS DA ORGANIZAÇÃO

### ✅ **Antes (Zona):**
- ❌ 15+ containers sem organização
- ❌ Difícil saber o que é o quê
- ❌ docker ps confuso
- ❌ Parar/iniciar arriscado

### ✅ **Agora (Organizado):**
- ✅ Stacks separadas por função
- ✅ Labels para filtrar
- ✅ Scripts helper (start, stop, status)
- ✅ Docker Compose por camada
- ✅ Fácil gerenciar
- ✅ Documentação clara

---

## 🎉 RESUMO

```
╔═══════════════════════════════════════════════╗
║  ✅ CONTAINERS ORGANIZADOS                    ║
╠═══════════════════════════════════════════════╣
║  Docker Compose:  ✅ 4 arquivos separados     ║
║  Scripts:         ✅ start, stop, status      ║
║  Labels:          ✅ Para filtrar             ║
║  Networks:        ✅ crm-network isolada      ║
║  Health Checks:   ✅ Automáticos              ║
║  Documentação:    ✅ GERENCIAR_CONTAINERS.md  ║
╠═══════════════════════════════════════════════╣
║  🎯 MUITO MAIS FÁCIL DE GERENCIAR!            ║
╚═══════════════════════════════════════════════╝
```

---

**Teste agora:**
```powershell
.\status-crm.ps1
```

**Veja a organização! 🎯**

