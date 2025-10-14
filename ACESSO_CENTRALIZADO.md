# 🌐 ACESSO CENTRALIZADO - Nginx Reverse Proxy

**Status**: ✅ ATIVO  
**Porta única**: 80  
**Arquitetura**: Profissional com reverse proxy

---

## 🎯 NOVO ACESSO (Porta 80 - Centralizada)

### 🏠 Acesso Principal
```
http://192.168.15.22
```

Tudo em uma única porta! Apenas mude o PATH:

### 📍 Endpoints Disponíveis

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend** | `http://192.168.15.22/` | Aplicação principal Next.js |
| **API** | `http://192.168.15.22/api/` | Backend Flask |
| **Grafana** | `http://192.168.15.22/grafana/` | Dashboards e métricas |
| **Prometheus** | `http://192.168.15.22/prometheus/` | Métricas brutas |
| **Health** | `http://192.168.15.22/health` | Status do sistema |

---

## ✅ VANTAGENS DA ARQUITETURA PROFISSIONAL

### 1. **Porta Única**
- Antes: 6 portas diferentes (3000, 5000, 3002, 9090, 3100, 5433)
- Agora: **1 porta** (80)
- Firewall: Liberar apenas porta 80/443

### 2. **URLs Amigáveis**
```
❌ Antes: http://192.168.15.22:3002
✅ Agora: http://192.168.15.22/grafana/
```

### 3. **Segurança**
- Rate limiting (proteção DDoS)
- Headers de segurança
- Centralização de autenticação (futuro)
- Logs centralizados

### 4. **Performance**
- Compressão gzip
- Cache de assets estáticos
- Connection pooling
- Load balancing (futuro)

### 5. **Preparado para SSL**
- Fácil adicionar HTTPS
- Certificados em um lugar só
- Let's Encrypt integrado

### 6. **Profissional**
- Arquitetura padrão de mercado
- Fácil escalar
- Fácil manutenção
- Fácil monitorar

---

## 🔧 CONFIGURAÇÃO TÉCNICA

### Nginx como Reverse Proxy

```
Cliente (Browser)
    ↓
Nginx (porta 80)
    ├─ / → Frontend (Next.js porta 3000)
    ├─ /api/ → Backend (Flask porta 5000)
    ├─ /grafana/ → Grafana (porta 3000 interna)
    └─ /prometheus/ → Prometheus (porta 9090 interna)
```

### Regras de Roteamento

**Path-based routing:**
- URL base (/) → Frontend
- URLs começando com /api/ → Backend
- URLs começando com /grafana/ → Grafana
- URLs começando com /prometheus/ → Prometheus

**Rewrite rules:**
```nginx
/api/health → http://localhost:5000/health
/grafana/dashboards → http://grafana:3000/dashboards
/prometheus/targets → http://prometheus:9090/targets
```

---

## 🚀 COMO USAR

### Do seu Mac/Safari:

**Antes (múltiplas portas):**
```
http://192.168.15.22:3000  # Frontend
http://192.168.15.22:5000  # API
http://192.168.15.22:3002  # Grafana
http://192.168.15.22:9090  # Prometheus
```

**Agora (porta única):**
```
http://192.168.15.22/              # Frontend
http://192.168.15.22/api/health    # API
http://192.168.15.22/grafana/      # Grafana
http://192.168.15.22/prometheus/   # Prometheus
```

---

## 📊 MONITORAMENTO DO NGINX

### Status do Nginx
```
http://192.168.15.22/nginx_status
```

Mostra:
- Conexões ativas
- Requisições/segundo
- Conexões aceitas/rejeitadas

### Logs
```powershell
# Logs de acesso
docker logs crm-nginx --tail 100

# Logs de erro
docker exec crm-nginx tail -f /var/log/nginx/error.log

# Ver conexões ativas
docker exec crm-nginx cat /var/log/nginx/access.log | tail -50
```

---

## 🔒 SEGURANÇA IMPLEMENTADA

### 1. Rate Limiting
- **API**: 10 requisições/segundo + burst de 20
- **Geral**: 50 requisições/segundo

Protege contra:
- DDoS
- Brute force
- Scraping agressivo

### 2. Headers de Segurança
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer-when-downgrade
```

### 3. Timeouts
- Conexão: 60s
- Envio: 60s (API: 300s para queries longas)
- Leitura: 60s (API: 300s)

---

## 🌟 PRÓXIMOS PASSOS (Opcional)

### 1. Adicionar HTTPS (SSL/TLS)
```powershell
# Gerar certificado auto-assinado (desenvolvimento)
.\gerar-ssl.ps1

# Ou usar Let's Encrypt (produção)
.\setup-letsencrypt.ps1
```

Após SSL:
```
https://192.168.15.22/
```

### 2. Adicionar Autenticação Centralizada
```nginx
# Basic Auth no Nginx
location /grafana/ {
    auth_basic "Área Restrita";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://grafana;
}
```

### 3. Domínio Customizado
```
# Editar hosts no Mac/Windows
192.168.15.22  crm.local

# Acessar
http://crm.local/
http://crm.local/grafana/
```

### 4. Load Balancing
```nginx
upstream api {
    server api-1:5000;
    server api-2:5000;
    server api-3:5000;
}
```

---

## 🔍 TROUBLESHOOTING

### Nginx não inicia
```powershell
# Ver logs
docker logs crm-nginx

# Testar configuração
docker exec crm-nginx nginx -t

# Recarregar config
docker exec crm-nginx nginx -s reload
```

### Erro 502 Bad Gateway
```powershell
# Verificar se serviços estão rodando
docker ps | grep -E "frontend|api|grafana|prometheus"

# Verificar conexão do Nginx com serviços
docker exec crm-nginx wget -O- http://host.docker.internal:3000
```

### Lentidão
```powershell
# Ver conexões ativas
docker exec crm-nginx cat /proc/net/tcp | wc -l

# Ver status
curl http://192.168.15.22/nginx_status
```

---

## 📝 COMANDOS ÚTEIS

### Iniciar/Parar
```powershell
# Iniciar
docker-compose -f docker-compose.nginx.yml up -d

# Parar
docker-compose -f docker-compose.nginx.yml down

# Reiniciar
docker-compose -f docker-compose.nginx.yml restart
```

### Logs
```powershell
# Logs em tempo real
docker logs -f crm-nginx

# Últimas 100 linhas
docker logs crm-nginx --tail 100

# Logs de acesso
docker exec crm-nginx tail -f /var/log/nginx/access.log
```

### Configuração
```powershell
# Testar config
docker exec crm-nginx nginx -t

# Recarregar sem downtime
docker exec crm-nginx nginx -s reload

# Ver config atual
docker exec crm-nginx cat /etc/nginx/nginx.conf
```

---

## 🎯 COMPARAÇÃO: ANTES vs AGORA

### ANTES (Múltiplas Portas)
```
❌ 6 portas diferentes expostas
❌ URLs complexas (IP:porta)
❌ Difícil de lembrar
❌ Firewall complexo (6 regras)
❌ Sem rate limiting
❌ Sem cache
❌ Logs dispersos
```

### AGORA (Reverse Proxy)
```
✅ 1 porta (80)
✅ URLs simples (/path)
✅ Fácil de lembrar
✅ Firewall simples (1 regra)
✅ Rate limiting ativo
✅ Cache de assets
✅ Logs centralizados
✅ Preparado para SSL
✅ Arquitetura profissional
```

---

## 🏆 BENEFÍCIOS PARA PRODUÇÃO

1. **Escalabilidade**: Fácil adicionar mais servidores backend
2. **Alta Disponibilidade**: Load balancing entre múltiplas instâncias
3. **Segurança**: Camada adicional de proteção
4. **Performance**: Cache e compressão
5. **Manutenção**: Atualizar serviços sem downtime
6. **Monitoramento**: Métricas centralizadas
7. **Conformidade**: Fácil adicionar autenticação/autorização

---

**🌐 ACESSE AGORA:**
```
http://192.168.15.22/
```

**Tudo em uma porta! Arquitetura profissional implementada! 🚀**

