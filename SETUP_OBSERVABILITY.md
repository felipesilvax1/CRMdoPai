# 📊 Guia de Configuração - Observabilidade e LocalStack

Este documento descreve como usar a stack completa de observabilidade e simulação AWS no projeto CRM.

## 🎯 Visão Geral

O ambiente de desenvolvimento agora inclui:

### **Aplicação**
- ✅ PostgreSQL (Banco de dados com 77M+ registros)
- ✅ Ollama (Engine LLM - Gemma)
- ✅ CRM API (Consultas ao banco)
- ✅ CRM LLM (Serviço de IA)
- ✅ Next.js Frontend (em desenvolvimento local)

### **Observabilidade**
- 📊 **Prometheus** - Coleta de métricas
- 📝 **Loki** - Agregação de logs
- 🔍 **Promtail** - Coleta de logs dos containers
- 📈 **Grafana** - Visualização e dashboards
- 📦 **cAdvisor** - Métricas de containers Docker

### **Simulação AWS**
- ☁️ **LocalStack** - Simula serviços AWS (S3, SQS, SNS, DynamoDB, Lambda)

---

## 🚀 Iniciando o Ambiente

### 1. Iniciar Todos os Serviços

```powershell
# Iniciar stack completa
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f
```

### 2. Iniciar Frontend (Desenvolvimento)

```powershell
cd next-app
npm install
npm run dev
```

O frontend estará disponível em: http://localhost:3000

---

## 📊 Acessando as Ferramentas

### **Grafana** - Dashboards e Visualização
- 🔗 URL: http://localhost:3002
- 👤 Login: `admin`
- 🔑 Senha: `admin`

**Primeiros Passos:**
1. Login com admin/admin
2. Explore os datasources pré-configurados (Prometheus e Loki)
3. Crie dashboards customizados

### **Prometheus** - Métricas
- 🔗 URL: http://localhost:9090
- 📊 Explore métricas em tempo real
- 🔍 Use PromQL para queries customizadas

**Métricas Disponíveis:**
```promql
# Buscas totais no CRM
crm_searches_total

# Duração de consultas LLM
crm_llm_query_duration_seconds

# Duração de consultas ao banco
crm_db_query_duration_seconds

# Erros na aplicação
crm_errors_total

# Usuários ativos
crm_active_users

# Requisições HTTP
crm_http_requests_total
```

### **Loki** - Logs
- 🔗 URL: http://localhost:3100
- 📝 Acesse via Grafana (Explore → Loki)

**Query de Logs:**
```logql
# Logs do CRM API
{container_name="crm-api"}

# Logs de erro
{level="ERROR"}

# Logs por stack
{stack="backend"}
```

### **cAdvisor** - Containers
- 🔗 URL: http://localhost:8080
- 📦 Métricas detalhadas de CPU, memória, rede e disco por container

### **LocalStack** - AWS Local
- 🔗 URL: http://localhost:4566
- ☁️ Simula serviços AWS localmente

---

## 🔧 Instrumentação da Aplicação

### Next.js - Métricas

O frontend Next.js está instrumentado com Prometheus:

#### **Endpoint de Métricas**
```
GET http://localhost:3000/api/metrics
```

#### **Health Check**
```
GET http://localhost:3000/api/health
```

#### **Como Usar Métricas no Código**

```typescript
import { recordSearch, recordDBQuery, recordError } from '../lib/metrics';

// Registrar uma busca
recordSearch('filtros', 'success');

// Registrar consulta ao banco
const startTime = Date.now();
// ... fazer consulta ...
const duration = (Date.now() - startTime) / 1000;
recordDBQuery('select_empresas', 'success', duration);

// Registrar erro
try {
  // código
} catch (error) {
  recordError('query_error', '/pagina');
}
```

---

## ☁️ LocalStack - AWS Simulada

### Recursos Criados Automaticamente

Ao iniciar, o LocalStack cria:

**S3 Buckets:**
- `cnae-reports-bucket` - Relatórios CNAE
- `crm-backups-bucket` - Backups
- `crm-exports-bucket` - Exports de dados

**SQS Queues:**
- `report-processing-queue` - Processamento de relatórios
- `notifications-queue` - Notificações
- `report-dlq` - Dead Letter Queue

**SNS Topics:**
- `crm-alerts` - Alertas do sistema
- `system-notifications` - Notificações

**DynamoDB Tables:**
- `query-cache` - Cache de consultas
- `user-sessions` - Sessões de usuário

### Usando LocalStack

#### **Via API Route**

```typescript
// Exemplo: Testar conexão
fetch('/api/s3-example?action=test')
  .then(res => res.json())
  .then(data => console.log(data));

// Upload de arquivo
fetch('/api/s3-example?action=upload', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fileName: 'relatorio.txt',
    content: 'Conteúdo do relatório',
    bucket: 'cnae-reports-bucket'
  })
});

// Listar arquivos
fetch('/api/s3-example?action=list&bucket=cnae-reports-bucket')
  .then(res => res.json())
  .then(data => console.log(data.files));
```

#### **Via AWS CLI (awslocal)**

```bash
# Instalar awslocal
pip install awscli-local

# Listar buckets
awslocal s3 ls

# Upload de arquivo
awslocal s3 cp arquivo.txt s3://cnae-reports-bucket/

# Listar filas SQS
awslocal sqs list-queues

# Listar tabelas DynamoDB
awslocal dynamodb list-tables
```

#### **No Código Next.js**

```typescript
import { s3Client, AWS_BUCKETS } from '../lib/awsClient';
import { PutObjectCommand } from '@aws-sdk/client-s3';

// Upload para S3/LocalStack
const command = new PutObjectCommand({
  Bucket: AWS_BUCKETS.REPORTS,
  Key: 'relatorio-2025.pdf',
  Body: pdfBuffer,
  ContentType: 'application/pdf',
});

await s3Client.send(command);
```

---

## 📈 Criando Dashboards no Grafana

### Dashboard Básico do CRM

1. Acesse Grafana (http://localhost:3002)
2. Dashboards → New Dashboard → Add Visualization
3. Selecione Prometheus como datasource
4. Use as queries abaixo:

#### **Painel 1: Buscas por Segundo**
```promql
rate(crm_searches_total[5m])
```

#### **Painel 2: Tempo Médio de Consulta LLM**
```promql
rate(crm_llm_query_duration_seconds_sum[5m]) / 
rate(crm_llm_query_duration_seconds_count[5m])
```

#### **Painel 3: Taxa de Erros**
```promql
rate(crm_errors_total[5m])
```

#### **Painel 4: Usuários Ativos**
```promql
crm_active_users
```

#### **Painel 5: Uso de CPU por Container**
```promql
rate(container_cpu_usage_seconds_total{container_label_stack="backend"}[5m])
```

#### **Painel 6: Uso de Memória**
```promql
container_memory_usage_bytes{container_label_stack="backend"} / 1024 / 1024
```

---

## 🔍 Troubleshooting

### Prometheus não está coletando métricas

```powershell
# Verificar se o Prometheus está rodando
docker-compose ps prometheus

# Ver logs do Prometheus
docker-compose logs prometheus

# Testar endpoint de métricas manualmente
curl http://localhost:3000/api/metrics
```

### LocalStack não está acessível

```powershell
# Verificar status
docker-compose ps localstack

# Ver logs
docker-compose logs localstack

# Testar conectividade
curl http://localhost:4566/_localstack/health
```

### Grafana não conecta aos datasources

1. Verifique se Prometheus e Loki estão rodando
2. Em Grafana, vá em Configuration → Data Sources
3. Teste a conexão de cada datasource
4. Verifique os logs: `docker-compose logs grafana`

---

## 🛠️ Comandos Úteis

```powershell
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (limpa dados)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart prometheus

# Ver logs de um serviço
docker-compose logs -f crm-api

# Ver métricas em tempo real
docker stats

# Rebuild de um serviço
docker-compose build crm-api
docker-compose up -d crm-api
```

---

## 📚 Próximos Passos

1. ✅ Criar dashboards customizados no Grafana
2. ✅ Configurar alertas no Prometheus
3. ✅ Instrumentar mais endpoints com métricas
4. ✅ Usar S3/LocalStack para armazenar relatórios
5. ✅ Implementar cache com DynamoDB/LocalStack
6. ✅ Criar filas SQS para processamento assíncrono

---

## 🎓 Recursos Adicionais

- [Documentação Prometheus](https://prometheus.io/docs/)
- [Documentação Grafana](https://grafana.com/docs/)
- [Documentação Loki](https://grafana.com/docs/loki/latest/)
- [LocalStack Docs](https://docs.localstack.cloud/)
- [AWS SDK JavaScript](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/)
- [Prom-client (Node.js)](https://github.com/siimon/prom-client)

---

**🎉 Ambiente pronto para desenvolvimento com observabilidade completa!**

