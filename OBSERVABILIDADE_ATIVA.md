# 📊 OBSERVABILIDADE ATIVA - Sistema CRM

**Status**: ✅ ONLINE  
**Iniciado**: 14/10/2025 13:15  
**Stack**: Prometheus + Grafana + Loki + Promtail

---

## 🎯 ACESSOS RÁPIDOS

### Grafana (Dashboards & Visualização)
- **URL**: http://192.168.15.22:3002
- **Login**: admin
- **Senha**: admin
- **Dashboards disponíveis**:
  - CRM Overview
  - API Performance
  - Database Metrics
  - User Activity

### Prometheus (Métricas)
- **URL**: http://192.168.15.22:9090
- **Targets**: http://192.168.15.22:9090/targets
- **Graph**: http://192.168.15.22:9090/graph

### Loki (Logs)
- **URL**: http://192.168.15.22:3100
- **Acesso via Grafana**: Explore → Loki

---

## 📈 MÉTRICAS COLETADAS

### 1. **Frontend Next.js** (porta 3000)
```
Endpoint: http://192.168.15.22:3000/api/metrics
```

**Métricas disponíveis:**
- `http_requests_total` - Total de requisições HTTP
- `http_request_duration_ms` - Duração das requisições (histogram)
- `page_views_total` - Visualizações de página
- `api_calls_total` - Chamadas à API
- `search_queries_total` - Buscas realizadas
- `user_actions_total` - Ações do usuário

**Labels:**
- `method` - Método HTTP (GET, POST, etc)
- `path` - Caminho da requisição
- `status` - Status code HTTP
- `user_id` - ID do usuário (se logado)

### 2. **Backend API** (porta 5000)
```
Endpoint: http://192.168.15.22:5000/metrics
```

**Métricas Flask padrão:**
- `flask_http_request_duration_seconds` - Duração das requests
- `flask_http_request_total` - Total de requests
- `process_cpu_seconds_total` - Uso de CPU
- `process_resident_memory_bytes` - Uso de memória

### 3. **PostgreSQL** (via postgres_exporter)
```
Se configurado: porta 9187
```

**Métricas de banco:**
- Conexões ativas
- Queries lentas
- Cache hit ratio
- Tamanho das tabelas
- Índices utilizados

### 4. **Docker Containers**
```
Se cAdvisor ativo: porta 8080
```

**Métricas de containers:**
- CPU usage
- Memory usage
- Network I/O
- Disk I/O

---

## 🔍 QUERIES ÚTEIS DO PROMETHEUS

### Performance da API
```promql
# Taxa de requisições por segundo
rate(http_requests_total[5m])

# Latência P95 (95% das requisições)
histogram_quantile(0.95, rate(http_request_duration_ms_bucket[5m]))

# Requisições com erro (5xx)
sum(rate(http_requests_total{status=~"5.."}[5m]))
```

### Performance da Busca Avançada
```promql
# Tempo médio de busca
rate(http_request_duration_ms_sum{path="/busca-avancada"}[5m]) / 
rate(http_request_duration_ms_count{path="/busca-avancada"}[5m])

# Total de buscas por minuto
rate(search_queries_total[1m]) * 60
```

### Performance do Sistema
```promql
# Uso de CPU
rate(process_cpu_seconds_total[5m]) * 100

# Uso de memória
process_resident_memory_bytes / 1024 / 1024  # MB
```

### Usuários Ativos
```promql
# Usuários únicos ativos (última hora)
count(count by (user_id) (http_requests_total{user_id!=""}[1h]))
```

---

## 📊 DASHBOARDS GRAFANA

### Dashboard 1: CRM Overview
**Painéis:**
- Requisições/segundo (tempo real)
- Latência média (P50, P95, P99)
- Taxa de erro
- Usuários ativos
- Buscas realizadas

### Dashboard 2: API Performance
**Painéis:**
- Endpoints mais lentos
- Endpoints mais chamados
- Distribuição de status codes
- Tempo de resposta por endpoint

### Dashboard 3: Database Performance
**Painéis:**
- Queries lentas (> 1s)
- Conexões ativas
- Cache hit ratio
- Tamanho das tabelas
- Uso de índices

### Dashboard 4: User Activity
**Painéis:**
- Páginas mais visitadas
- Ações mais realizadas
- Filtros mais usados
- Tempo médio de sessão

---

## 🔔 ALERTAS CONFIGURADOS

### Alerta 1: API Lenta
```yaml
Condição: Latência P95 > 5s por 5 minutos
Severidade: WARNING
Ação: Notificação no console
```

### Alerta 2: Taxa de Erro Alta
```yaml
Condição: Erros 5xx > 5% das requisições
Severidade: CRITICAL
Ação: Notificação + log detalhado
```

### Alerta 3: Uso de Memória Alto
```yaml
Condição: Memória > 80% por 10 minutos
Severidade: WARNING
Ação: Notificação
```

---

## 📝 LOGS (Loki + Promtail)

### Acessar logs no Grafana:
1. Acesse Grafana: http://192.168.15.22:3001
2. Menu lateral: **Explore**
3. Selecione datasource: **Loki**
4. Query de exemplo:

```logql
# Todos os logs da API
{container_name="crm-api"}

# Logs de erro
{container_name="crm-api"} |= "ERROR"

# Logs de uma rota específica
{container_name="crm-api"} |= "/busca-avancada"

# Logs por tempo de resposta
{container_name="crm-api"} |= "ms" | json | response_time > 1000
```

### Logs do Frontend:
```logql
# Todos os logs Next.js
{job="nextjs"}

# Erros no frontend
{job="nextjs"} |= "Error"

# Performance logs
{job="nextjs"} |= "PERFORMANCE"
```

---

## 🛠️ COMANDOS ÚTEIS

### Verificar Status
```powershell
# Status dos containers
docker ps --filter "name=prometheus" --filter "name=grafana"

# Logs do Prometheus
docker logs prometheus --tail 50

# Logs do Grafana
docker logs grafana --tail 50
```

### Reiniciar Serviços
```powershell
# Reiniciar Prometheus
docker-compose restart prometheus

# Reiniciar Grafana
docker-compose restart grafana

# Reiniciar tudo
docker-compose restart prometheus grafana loki promtail
```

### Verificar Targets do Prometheus
```powershell
# Via curl
curl http://localhost:9090/api/v1/targets | ConvertFrom-Json

# Via browser
Start-Process "http://localhost:9090/targets"
```

---

## 🎯 TROUBLESHOOTING

### Grafana não carrega dashboards
```powershell
# Verificar logs
docker logs grafana --tail 50

# Recriar dashboards
docker-compose restart grafana
```

### Prometheus não coleta métricas
```powershell
# Verificar targets
curl http://localhost:9090/api/v1/targets

# Verificar config
docker exec prometheus cat /etc/prometheus/prometheus.yml

# Recarregar config
curl -X POST http://localhost:9090/-/reload
```

### Loki não recebe logs
```powershell
# Verificar Promtail
docker logs promtail --tail 50

# Verificar conexão
curl http://localhost:3100/ready
```

---

## 📊 MÉTRICAS CUSTOMIZADAS

### Como adicionar novas métricas:

**No Frontend (Next.js):**
```javascript
// pages/sua-pagina.jsx
import { incrementCounter, recordHistogram } from '@/lib/metrics';

// Incrementar contador
incrementCounter('custom_action_total', { action: 'click', page: 'home' });

// Registrar tempo
recordHistogram('custom_duration_ms', duration, { operation: 'search' });
```

**Na API (Flask):**
```python
# api/app.py
from prometheus_client import Counter, Histogram

custom_counter = Counter('custom_api_action', 'Description', ['action'])
custom_counter.labels(action='query').inc()
```

---

## 🔐 SEGURANÇA

### Grafana
- **Login**: admin / admin
- **Trocar senha**: http://192.168.15.22:3001/profile/password
- **Adicionar usuários**: Settings → Users

### Prometheus
- **Sem autenticação** (apenas rede interna)
- **Produção**: Adicionar Nginx com auth

---

## 📱 ACESSO REMOTO

### Do Mac/Celular:
```
Grafana: http://192.168.15.22:3001
Prometheus: http://192.168.15.22:9090
```

### Firewall (se necessário):
```powershell
# Liberar porta 3001 (Grafana)
New-NetFirewallRule -DisplayName "Grafana" -Direction Inbound -LocalPort 3001 -Protocol TCP -Action Allow

# Liberar porta 9090 (Prometheus)
New-NetFirewallRule -DisplayName "Prometheus" -Direction Inbound -LocalPort 9090 -Protocol TCP -Action Allow
```

---

## 📈 PRÓXIMOS PASSOS

1. ✅ Grafana configurado
2. ✅ Prometheus coletando métricas
3. ✅ Loki agregando logs
4. ⏳ Criar alertas customizados
5. ⏳ Dashboard de migração do BD
6. ⏳ Métricas de performance pós-índices

---

**🎯 TUDO PRONTO PARA MONITORAR A SAÚDE DO SISTEMA!**

**Acesse Grafana agora:** http://192.168.15.22:3001  
**Login:** admin / admin

