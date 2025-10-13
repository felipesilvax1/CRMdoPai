# 🚀 Guia de Início Rápido - Observabilidade

## ⚡ Start Rápido (3 comandos)

```powershell
# 1. Iniciar stack de observabilidade (sem afetar PostgreSQL)
docker-compose up -d prometheus loki promtail grafana cadvisor localstack

# 2. Iniciar frontend em desenvolvimento
cd next-app
npm run dev
```

**Pronto!** Acesse http://localhost:3002 (Grafana: admin/admin)

---

## 📊 Serviços Iniciados

✅ **Prometheus** - http://localhost:9090  
✅ **Loki** - http://localhost:3100  
✅ **Promtail** - Coleta logs dos containers  
✅ **Grafana** - http://localhost:3002 (admin/admin)  
✅ **cAdvisor** - http://localhost:8080  
✅ **LocalStack** - http://localhost:4566  

✅ **Frontend** - http://localhost:3000  
✅ **Métricas** - http://localhost:3000/api/metrics  
✅ **Health** - http://localhost:3000/api/health  

---

## 🎯 O que NÃO foi iniciado

❌ **PostgreSQL** - Você já tem rodando (cnpj_postgres_final)  
❌ **Ollama** - Você já tem rodando  
❌ **CRM API** - Pode iniciar depois: `docker-compose up -d crm-api`  
❌ **CRM LLM** - Pode iniciar depois: `docker-compose up -d crm-llm`  

---

## 📈 Primeiro Dashboard no Grafana

1. Acesse http://localhost:3002
2. Login: `admin` / Senha: `admin`
3. Menu lateral → Dashboards → CRM - Overview Dashboard
4. Visualize métricas em tempo real!

### Dashboard Inclui:
- 📊 Taxa de buscas por segundo
- ⏱️ Tempo médio de consulta LLM
- 👥 Usuários ativos
- ❌ Taxa de erros
- 💻 Uso de CPU por serviço
- 🧠 Uso de memória por serviço

---

## 🔍 Testando Métricas

### Via Browser:
```
http://localhost:3000/api/metrics
```

### Via PowerShell:
```powershell
# Ver métricas do Next.js
curl http://localhost:3000/api/metrics

# Ver health check
curl http://localhost:3000/api/health

# Testar LocalStack
curl http://localhost:4566/_localstack/health
```

---

## ☁️ Testando LocalStack

### Via API do Next.js:
```javascript
// No console do browser (localhost:3000)
fetch('/api/s3-example?action=test')
  .then(r => r.json())
  .then(console.log)

// Listar buckets
fetch('/api/s3-example?action=list&bucket=cnae-reports-bucket')
  .then(r => r.json())
  .then(console.log)
```

### Via awslocal (CLI):
```powershell
# Instalar
pip install awscli-local

# Listar buckets S3
awslocal s3 ls

# Listar filas SQS
awslocal sqs list-queues

# Listar tabelas DynamoDB
awslocal dynamodb list-tables
```

---

## 🔧 Comandos Úteis

### Ver Status:
```powershell
docker-compose ps
```

### Ver Logs em Tempo Real:
```powershell
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f localstack
```

### Reiniciar um Serviço:
```powershell
docker-compose restart grafana
```

### Parar Observabilidade (sem afetar PostgreSQL):
```powershell
docker-compose stop prometheus loki promtail grafana cadvisor localstack
```

### Parar Tudo:
```powershell
docker-compose down
```

---

## 📊 Queries Úteis no Prometheus

Acesse http://localhost:9090 e experimente:

```promql
# Buscas totais
crm_searches_total

# Taxa de buscas por segundo (últimos 5min)
rate(crm_searches_total[5m])

# Tempo médio de consulta LLM
rate(crm_llm_query_duration_seconds_sum[5m]) / 
rate(crm_llm_query_duration_seconds_count[5m])

# Usuários ativos agora
crm_active_users

# Erros nas últimas 5 minutos
increase(crm_errors_total[5m])

# Uso de CPU dos containers backend
rate(container_cpu_usage_seconds_total{container_label_stack="backend"}[5m]) * 100

# Uso de memória dos containers backend (MB)
container_memory_usage_bytes{container_label_stack="backend"} / 1024 / 1024
```

---

## 🔍 Logs no Grafana (Loki)

1. Acesse Grafana (http://localhost:3002)
2. Menu lateral → Explore
3. Selecione datasource: **Loki**
4. Use queries LogQL:

```logql
# Todos os logs do CRM API
{container_name="crm-api"}

# Logs de erro
{level="ERROR"}

# Logs do backend
{stack="backend"}

# Logs de um container específico nas últimas 5 minutos
{container_name="crm-llm"} |= "error" 
```

---

## ✨ Próximos Passos

### 1. Quando terminar a importação do BD:

```powershell
# Iniciar API e LLM
docker-compose up -d crm-api crm-llm

# Ver logs
docker-compose logs -f crm-api crm-llm
```

### 2. Instrumentar suas páginas:

```typescript
// Em qualquer página Next.js
import { recordSearch, recordDBQuery } from '../lib/metrics';

// Ao fazer uma busca
recordSearch('filtros', 'success');

// Ao consultar o banco
const start = Date.now();
// ... query ...
recordDBQuery('select_empresas', 'success', (Date.now() - start) / 1000);
```

### 3. Criar mais dashboards no Grafana:
- Dashboard de performance do banco
- Dashboard de uso por usuário
- Dashboard de relatórios gerados

### 4. Usar LocalStack para funcionalidades reais:
- Salvar relatórios em S3
- Implementar filas de processamento
- Cache com DynamoDB

---

## 🆘 Troubleshooting

### Grafana não abre:
```powershell
# Ver logs
docker-compose logs grafana

# Reiniciar
docker-compose restart grafana
```

### Prometheus não coleta métricas do Next.js:
1. Certifique-se que o frontend está rodando (`npm run dev`)
2. Teste: http://localhost:3000/api/metrics
3. Verifique `prometheus/prometheus.yml`

### LocalStack não está acessível:
```powershell
# Ver logs
docker-compose logs localstack

# Testar
curl http://localhost:4566/_localstack/health
```

---

## 📚 Documentação Completa

Ver `SETUP_OBSERVABILITY.md` para guia detalhado.

---

**🎉 Ambiente de observabilidade pronto!**

Enquanto o BD importa, você já pode explorar Grafana, Prometheus e LocalStack! 🚀

