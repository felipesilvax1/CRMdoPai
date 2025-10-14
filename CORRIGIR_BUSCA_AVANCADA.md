# 🔧 Como Corrigir o Dropdown de Estados na Busca Avançada

## 🎯 Problema
Os estados não aparecem no dropdown porque:
1. ❌ Firewall do Windows bloqueia a porta 5000
2. ❌ Frontend não está configurado para usar o IP correto

---

## ✅ Solução em 3 Passos

### **PASSO 1: Liberar Firewall**

Execute o script com **Administrador**:

```powershell
# Clique com botão direito no PowerShell → "Executar como Administrador"
.\liberar-porta-5000.ps1
```

Ou execute manualmente:
```powershell
New-NetFirewallRule -DisplayName "CRM API (5000)" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Any
```

---

### **PASSO 2: Configurar Frontend**

Crie/edite o arquivo `next-app/.env.local`:

```bash
# Modo de desenvolvimento
NEXT_PUBLIC_DEV_MODE=true

# URL da API (use o IP da sua máquina)
NEXT_PUBLIC_API_URL=http://192.168.15.22:5000

# URL do LLM
NEXT_PUBLIC_LLM_URL=http://192.168.15.22:8000
```

---

### **PASSO 3: Reiniciar Frontend**

```bash
cd next-app
# Pare o servidor (Ctrl+C)
# Reinicie:
npm run dev
```

---

## 🧪 Testar

### 1. Testar API diretamente:
```bash
curl http://192.168.15.22:5000/filtros/ufs
```

**Deve retornar:** JSON com todos os estados brasileiros

### 2. Testar no navegador:
```
http://192.168.15.22:3000/busca-avancada
```

**Clique no dropdown "Estado (UF)"** → Deve aparecer todos os 27 estados!

---

## 🚨 Se ainda não funcionar

### Verificar logs da API:
```bash
docker logs crm-api
```

### Verificar console do navegador:
```
F12 → Console → Procure por erros
```

### Testar conectividade:
```powershell
Test-NetConnection -ComputerName 192.168.15.22 -Port 5000
# TcpTestSucceeded deve ser True
```

---

## 📊 Status Atual

✅ API conectada no banco correto: `cnpj_processado`  
✅ Dados importados: 182M registros  
✅ Endpoint `/filtros/ufs` retorna dados corretamente  
❌ Firewall bloqueando acesso remoto  
❌ Frontend sem configuração de IP  

---

## 💡 Dica

Se você acessa apenas de `localhost`, pode usar:
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

Mas se acessa do Mac ou outro dispositivo, **precisa usar o IP** (`192.168.15.22`)!


