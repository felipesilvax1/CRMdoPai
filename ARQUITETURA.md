# 🏗️ Arquitetura do Sistema CRM - CNPJ

## 📊 Visão Geral

Sistema profissional para consulta de dados da Receita Federal com 77+ milhões de empresas, usando arquitetura moderna com containers Docker.

## 🎯 Componentes

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  NAVEGADOR (localhost:3000)                         │
│  Frontend Next.js + React + Tailwind                │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST API
                   ▼
┌─────────────────────────────────────────────────────┐
│  CONTAINER: crm-api (localhost:5000)                 │
│  ├─ Flask REST API                                  │
│  ├─ CORS habilitado                                 │
│  ├─ Health check /health                            │
│  └─ Query endpoint /query                           │
└──────────────────┬──────────────────────────────────┘
                   │ PostgreSQL/SQLite
                   ▼
┌─────────────────────────────────────────────────────┐
│  BANCO DE DADOS                                      │
│  ├─ PostgreSQL (Supabase) - Porta 54322            │
│  └─ SQLite (Backup) - 32GB local                   │
└─────────────────────────────────────────────────────┘
```

## 🐳 Estrutura Docker

### Opção 1: Stack Completo (Recomendado)

```bash
# Iniciar tudo
docker compose up --build

# Apenas API
docker compose up --build api

# Apenas Frontend
docker compose up --build next-app
```

### Opção 2: Desenvolvimento Local

```bash
# Backend API
cd api
pip install -r requirements.txt
python app.py

# Frontend
npm install
npm run dev
```

## 📁 Estrutura de Arquivos

```
CRM/
├── api/                          # Backend Flask
│   ├── Dockerfile               # Container da API
│   ├── app.py                   # Aplicação principal
│   ├── requirements.txt         # Dependências Python
│   └── .env                     # Variáveis de ambiente
│
├── app/                         # Frontend Next.js
│   ├── layout.tsx              # Layout principal
│   ├── page.tsx                # Página inicial
│   └── globals.css             # Estilos
│
├── docker-compose.yml          # Orquestração dos containers
├── Dockerfile                  # Container do Next.js
├── migrar_para_postgres.py    # Script de migração
├── CNPJ_Processado.db         # Banco SQLite (32GB)
└── README.md                   # Documentação

```

## 🔧 Configuração

### Variáveis de Ambiente (API)

```env
DB_HOST=host.docker.internal    # Ou supabase_db_PwC
DB_PORT=54322                   # Porta do PostgreSQL
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
```

### Portas Utilizadas

| Serviço | Porta | URL |
|---------|-------|-----|
| Frontend | 3000 | http://localhost:3000 |
| API | 5000 | http://localhost:5000 |
| PostgreSQL | 54322 | localhost:54322 |
| Supabase Studio | 54323 | http://localhost:54323 |

## 🚀 Início Rápido

### 1. Com Dados no SQLite (Atual)

```bash
# Iniciar apenas o frontend
docker compose up next-app

# Em outro terminal, iniciar a API com SQLite
python api_sqlite.py
```

### 2. Migrar para PostgreSQL (Profissional)

```bash
# 1. Migrar dados (pode levar horas!)
python migrar_para_postgres.py

# 2. Iniciar stack completo
docker compose up --build
```

## 📡 Endpoints da API

### Health Check
```http
GET http://localhost:5000/health

Response:
{
  "status": "ok",
  "database": "connected",
  "database_type": "PostgreSQL",
  "message": "API funcionando!"
}
```

### Consulta
```http
POST http://localhost:5000/query
Content-Type: application/json

{
  "question": "Quantas empresas temos?"
}

Response:
{
  "resposta_texto": "No banco temos 77,041,156 empresas...",
  "sql_gerado": "SELECT COUNT(*) FROM empresas",
  "total_resultados": 1,
  "dados_completos": [...]
}
```

## 🎨 Frontend

### Tecnologias
- **Next.js 14** (App Router)
- **React 18** (Client Components)
- **Tailwind CSS** (Estilização)
- **TypeScript** (Tipagem)

### Funcionalidades
- ✅ Consulta em linguagem natural
- ✅ Visualização de dados em tabela
- ✅ Exportação CSV/PDF
- ✅ SQL gerado visível
- ✅ Contagem de resultados

## 🗄️ Banco de Dados

### Tabelas Principais

1. **empresas** (77M registros)
   - cnpj basico (PK)
   - razao social
   - porte empresa
   - natureza juridica

2. **estabelecimentos** (79M registros)
   - cnpj completo
   - municipio, uf
   - cnae_fiscal_principal

3. **socios** (26M registros)
   - nome socio
   - cnpj basico (FK)

4. **cnaes** (2.7K registros)
   - codigo (PK)
   - descricao

## 🔒 Segurança

- ✅ CORS configurado
- ✅ Queries SQL parametrizadas
- ✅ Validação de entrada
- ✅ Health checks
- ✅ Logs estruturados

## 🐛 Troubleshooting

### API não conecta ao banco
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep supabase_db

# Testar conexão
docker exec supabase_db_PwC psql -U postgres -c "SELECT 1"
```

### Frontend não carrega
```bash
# Verificar logs
docker logs crm-frontend

# Reconstruir
docker compose up --build next-app
```

### Porta em uso
```bash
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :5000

# Matar processo
taskkill /PID <PID> /F
```

## 📈 Performance

### Recomendações
- Use índices nas colunas de busca frequente
- Limite resultados com LIMIT
- Cache de queries comuns
- Connection pooling

### Migração Otimizada
- Batch size: 10.000 registros
- Commit por batch
- Índices criados após inserção
- Progress bar em tempo real

## 🔄 Próximos Passos

1. ✅ **Estrutura dockerizada criada**
2. ⏳ **Migração SQLite → PostgreSQL** (opcional, lento)
3. 🔜 **Implementar IA real** (Ollama/OpenAI)
4. 🔜 **Cache de consultas**
5. 🔜 **Autenticação**

## 📞 Support

Para problemas ou sugestões:
1. Verificar logs: `docker logs crm-api`
2. Health check: `curl http://localhost:5000/health`
3. Logs do PostgreSQL: `docker logs supabase_db_PwC`

## 📝 Notas

- O banco SQLite (32GB) contém todos os dados
- Migração para PostgreSQL é opcional mas recomendada
- Sistema funciona 100% com SQLite atualmente
- PostgreSQL permite queries mais avançadas e performance

---

**Status Atual**: ✅ Frontend + API funcionando com SQLite
**Próximo**: Migração para PostgreSQL (opcional)


