# 🌐 Acesso Remoto - Do Mac/Outros Dispositivos

Guia para acessar os serviços do PC Windows a partir do Mac, tablet ou outros dispositivos na mesma rede.

---

## 📡 **Passo 1: Descobrir IP do PC Windows**

No PowerShell do Windows:

```powershell
# Opção 1: Ver todos os IPs
ipconfig

# Opção 2: Apenas IPv4 (mais limpo)
ipconfig | Select-String -Pattern "IPv4"

# Opção 3: Direto do Wi-Fi
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi").IPAddress
```

**Anote o IP**, algo como: `192.168.15.123` ou `192.168.1.XX`

---

## 🔓 **Passo 2: Liberar Firewall (se necessário)**

### **Opção A: Script Automatizado (Recomendado)**

Execute no PowerShell como **Administrador**:

```powershell
.\liberar-firewall.ps1
```

Este script irá:
- ✅ Liberar todas as portas necessárias
- ✅ Mostrar seu IP automaticamente
- ✅ Dar as URLs prontas para acessar

### **Opção B: Manual**

Se preferir liberar manualmente:

```powershell
# Grafana
New-NetFirewallRule -DisplayName "CRM - Grafana" -Direction Inbound -Protocol TCP -LocalPort 3002 -Action Allow

# Prometheus
New-NetFirewallRule -DisplayName "CRM - Prometheus" -Direction Inbound -Protocol TCP -LocalPort 9090 -Action Allow

# Frontend
New-NetFirewallRule -DisplayName "CRM - Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow

# API
New-NetFirewallRule -DisplayName "CRM - API" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow

# LLM
New-NetFirewallRule -DisplayName "CRM - LLM" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# cAdvisor
New-NetFirewallRule -DisplayName "CRM - cAdvisor" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow

# LocalStack
New-NetFirewallRule -DisplayName "CRM - LocalStack" -Direction Inbound -Protocol TCP -LocalPort 4566 -Action Allow
```

---

## 🍎 **Passo 3: Acessar do Mac (Safari/Chrome)**

Substitua `192.168.15.XX` pelo **IP do seu PC**:

### **URLs de Acesso:**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Grafana** ⭐ | `http://192.168.15.XX:3002` | Dashboards (admin/admin) |
| **Prometheus** | `http://192.168.15.XX:9090` | Métricas |
| **Frontend** | `http://192.168.15.XX:3000` | Aplicação CRM |
| **API** | `http://192.168.15.XX:5000` | API de dados |
| **LLM** | `http://192.168.15.XX:8000` | Serviço de IA |
| **cAdvisor** | `http://192.168.15.XX:8080` | Containers |
| **LocalStack** | `http://192.168.15.XX:4566` | AWS simulada |

---

## 🎯 **Exemplo Prático:**

Se seu IP for `192.168.15.24`:

```
✅ Grafana:    http://192.168.15.24:3002
✅ Prometheus: http://192.168.15.24:9090
✅ Frontend:   http://192.168.15.24:3000
```

---

## 📱 **Funciona em:**

- ✅ Mac (Safari, Chrome, Firefox)
- ✅ iPhone/iPad (Safari)
- ✅ Outro PC na mesma rede
- ✅ Tablet Android
- ✅ Qualquer dispositivo na mesma rede Wi-Fi

---

## 🔧 **Troubleshooting**

### **Problema 1: Não consigo acessar**

✅ **Verificar se os serviços estão rodando no PC:**
```powershell
docker-compose ps
```

✅ **Testar acesso local primeiro:**
```powershell
# No PC Windows, teste se funciona localmente
curl http://localhost:3002
```

✅ **Verificar firewall:**
```powershell
# Listar regras do firewall do CRM
Get-NetFirewallRule -DisplayName "CRM*"
```

✅ **Verificar se está na mesma rede:**
- Mac e PC devem estar na mesma rede Wi-Fi
- Não funciona se estiver usando VPN

### **Problema 2: "Connection refused"**

Provavelmente o firewall está bloqueando. Execute:
```powershell
.\liberar-firewall.ps1
```

### **Problema 3: "Timeout" ou demora muito**

Pode ser configuração do roteador. Tente:
1. Reiniciar o roteador
2. Verificar se o PC não está em "Rede pública" (use "Rede privada")
3. Desabilitar temporariamente antivírus/firewall para teste

### **Problema 4: IP mudou**

Se o IP do PC mudar (comum com DHCP):

**Opção A: Ver IP atual:**
```powershell
ipconfig | Select-String -Pattern "IPv4"
```

**Opção B: Configurar IP fixo no roteador:**
1. Acesse configurações do roteador
2. Procure "DHCP Reservation" ou "IP estático"
3. Vincule o MAC address do PC a um IP fixo

---

## 🌟 **Dicas:**

### **1. Salvar favoritos no Safari:**

Adicione aos favoritos do Mac para acesso rápido:
- 📊 Grafana: `http://192.168.15.XX:3002`
- 📈 Prometheus: `http://192.168.15.XX:9090`

### **2. Usar hostname em vez de IP (opcional):**

No Mac, adicione ao `/etc/hosts`:
```bash
sudo nano /etc/hosts
```

Adicione:
```
192.168.15.XX    crm-pc
```

Depois acesse:
- `http://crm-pc:3002` (Grafana)
- `http://crm-pc:9090` (Prometheus)

### **3. Criar atalhos no iPhone:**

No Safari do iPhone:
1. Acesse `http://192.168.15.XX:3002`
2. Toque no botão "Compartilhar"
3. "Adicionar à Tela de Início"
4. Terá um ícone do Grafana na home!

---

## 📊 **Dashboards Recomendados no Mac:**

### **No Grafana (melhor experiência):**

1. **CRM - Overview Dashboard** - Já está criado! ⭐
2. **Explore** - Ver logs em tempo real
3. **Alertas** - Configurar notificações

### **No Prometheus (queries avançadas):**

```promql
# Ver buscas em tempo real
rate(crm_searches_total[5m])

# Ver uso de memória
container_memory_usage_bytes / 1024 / 1024

# Ver CPU
rate(container_cpu_usage_seconds_total[5m]) * 100
```

---

## 🔒 **Segurança:**

⚠️ **IMPORTANTE:** Essas portas estão liberadas apenas na rede local (192.168.x.x)

✅ **Seguro:**
- Acesso apenas dentro da sua rede Wi-Fi
- Não está exposto na internet

❌ **NÃO recomendado:**
- Não expor essas portas diretamente na internet
- Se precisar acesso externo, use VPN

---

## 🚀 **Comandos Úteis:**

### **Ver IP rapidamente:**
```powershell
# PC Windows
hostname
ipconfig | Select-String "IPv4"
```

```bash
# Mac (para comparar rede)
ifconfig | grep "inet "
```

### **Testar conectividade do Mac:**
```bash
# Testar se o PC está acessível
ping 192.168.15.XX

# Testar porta específica
nc -zv 192.168.15.XX 3002
```

---

## 📱 **Exemplo de Uso:**

**Cenário:** Você está trabalhando no Mac, mas o banco de dados está rodando no PC Windows.

**Workflow:**
1. ✅ PC Windows: Roda Docker com todos os serviços
2. ✅ Mac: Acessa via Safari para visualizar dashboards
3. ✅ Desenvolve no Mac usando VSCode
4. ✅ Frontend roda no PC, mas acessa do Mac
5. ✅ Monitora tudo pelo Grafana no Mac! 🎉

---

## 🎨 **Interface Responsiva:**

Todos os serviços funcionam bem em telas menores:
- ✅ Grafana - Totalmente responsivo
- ✅ Prometheus - Funciona bem no mobile
- ✅ Frontend Next.js - Tailwind CSS responsivo

---

## 💡 **Exemplo Completo:**

```powershell
# 1. No PC Windows - Liberar firewall
.\liberar-firewall.ps1

# 2. Anotar o IP mostrado (ex: 192.168.15.24)

# 3. No PC Windows - Iniciar serviços
.\start-observability.ps1

# 4. No Mac Safari - Acessar
# http://192.168.15.24:3002
# Login: admin / admin

# 5. Explorar dashboards! 🎉
```

---

**🌐 Pronto! Agora você pode monitorar o CRM de qualquer dispositivo na sua rede!**

**Dica:** O Grafana no iPad/Mac com tela grande é perfeito para dashboards! 📊✨

