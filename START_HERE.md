# 🚀 START HERE - Guia de Início Rápido

## ⚡ Como iniciar o sistema CRM completo

### **Opção 1: Desenvolvimento (Recomendado)** 🔧

```powershell
# 1. Verificar o que está rodando
.\check-services.ps1

# 2. Iniciar observabilidade (Grafana, Prometheus, etc)
.\start-observability.ps1

# 3. Iniciar API (se necessário)
docker-compose up -d crm-api

# 4. Iniciar frontend (em outro terminal)
cd next-app
npm run dev
```

Acesse:
- 🎛️ **Admin Console:** http://localhost:3000/admin-console
- 🌐 **Frontend:** http://localhost:3000
- 📊 **Grafana:** http://localhost:3002 (admin/admin)

---

### **Opção 2: Stack Completa** 🎁

```powershell
# Inicia TUDO de uma vez
docker-compose -f docker-compose.all.yml up -d

# Frontend em dev (em outro terminal)
cd next-app
npm run dev
```

---

### **Opção 3: Apenas Observabilidade** 👁️

```powershell
# Grafana + Prometheus + Loki + LocalStack
.\start-observability.ps1

# Frontend
cd next-app
npm run dev
```

---

## 🔍 **Verificação de Saúde**

```powershell
# Ver status de todos os serviços
.\check-services.ps1

# Validar código antes de commit
.\validate-all.ps1
```

---

## 📊 **URLs Principais**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Admin Console** | http://localhost:3000/admin-console | ⭐ Central de controle |
| **Frontend** | http://localhost:3000 | Aplicação CRM |
| **Grafana** | http://localhost:3002 | Dashboards (admin/admin) |
| **Prometheus** | http://localhost:9090 | Métricas |
| **API** | http://localhost:5000 | API de dados |
| **LLM** | http://localhost:8000 | Serviço de IA |

---

## ⚠️ **Mensagens Comuns**

### **"Não foi possível conectar à API"**
✅ **NORMAL** - A API não está rodando

**Solução:**
```powershell
docker-compose up -d crm-api
```

### **"0 de 8 serviços online"**
✅ **NORMAL** - Serviços não foram iniciados ainda

**Solução:**
```powershell
.\start-observability.ps1
```

---

## 🎯 **Workflow Recomendado**

### **Desenvolvimento Diário:**
1. `.\check-services.ps1` - Ver o que está rodando
2. `cd next-app && npm run dev` - Iniciar frontend
3. Trabalhar no código
4. `.\validate-all.ps1` - Validar antes de commit
5. `git add . && git commit -m "..."` - Commit

### **Primeira Vez:**
1. `npm install` (na raiz e em next-app)
2. `.\start-observability.ps1` - Iniciar infra
3. `docker-compose up -d crm-api` - Iniciar API
4. `cd next-app && npm run dev` - Frontend
5. Abrir http://localhost:3000/admin-console

---

## 🐳 **Gerenciamento Docker**

```powershell
# Ver containers rodando
docker-compose ps

# Ver logs
docker-compose logs -f crm-api

# Parar tudo
docker-compose down

# Parar observabilidade
.\stop-observability.ps1

# Reiniciar um serviço
docker-compose restart crm-api
```

---

## 🍎 **Acessar do Mac**

```powershell
# 1. No PC Windows, liberar firewall
.\liberar-firewall.ps1

# 2. Ver seu IP
ipconfig | Select-String "IPv4"

# 3. No Mac Safari
# http://192.168.15.XX:3000/admin-console
```

---

## 🧪 **Testes e Validação**

```powershell
# Validação completa (todos os testes)
.\validate-all.ps1

# Validação rápida (pre-commit)
.\pre-commit.ps1

# Apenas testes do frontend
cd next-app
npm test

# Build de produção
cd next-app
npm run build
```

---

## 📚 **Documentação**

| Arquivo | Descrição |
|---------|-----------|
| `START_HERE.md` | ⭐ Este arquivo - comece aqui |
| `ADMIN_CONSOLE.md` | Guia da console de admin |
| `SETUP_OBSERVABILITY.md` | Observabilidade completa |
| `CI_CD_GUIDE.md` | Pipeline de CI/CD |
| `ACESSO_REMOTO.md` | Acessar do Mac/outros |
| `INICIAR_OBSERVABILIDADE.md` | Guia rápido de observabilidade |

---

## 🆘 **Problemas Comuns**

### **Frontend não carrega:**
```powershell
# Reinstalar dependências
cd next-app
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### **API não responde:**
```powershell
# Verificar se está rodando
docker-compose ps

# Ver logs
docker-compose logs crm-api

# Reiniciar
docker-compose restart crm-api
```

### **Erro de hydration no Next.js:**
✅ **JÁ CORRIGIDO** - Recarregue a página (Ctrl+F5)

### **Porta já está em uso:**
```powershell
# Ver o que está usando a porta
netstat -ano | findstr :3000

# Matar processo (substitua PID)
taskkill /PID <numero> /F
```

---

## 🎉 **Pronto!**

**Comando mágico para iniciar tudo:**
```powershell
.\check-services.ps1 && .\start-observability.ps1 && cd next-app && npm run dev
```

**Acesse:**
🎛️ http://localhost:3000/admin-console

---

**💡 Dica:** Adicione a Admin Console aos favoritos!

**❓ Dúvida?** Leia a documentação específica acima.

