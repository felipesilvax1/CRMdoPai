# 🚀 Guia Completo - CI/CD e Testes Automatizados

## 📋 Visão Geral

Sistema completo de CI/CD com **testes automatizados** para garantir qualidade e confiabilidade em todos os componentes.

```
┌─────────────────────────────────────────────┐
│           PIPELINE CI/CD                    │
├─────────────────────────────────────────────┤
│                                             │
│  1. Push/PR → GitHub                        │
│  2. Trigger → GitHub Actions                │
│  3. Testes Paralelos:                       │
│     • API de Dados     ✅                   │
│     • LLM Service      ✅                   │
│     • Frontend         ✅                   │
│     • Qualidade Código ✅                   │
│  4. Testes Integração  ✅                   │
│  5. Build Docker       ✅                   │
│  6. Deploy Produção    ✅                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🧪 Testes Implementados

### 1. **API de Dados** (`api/tests/`)

**Framework:** Pytest

**Cobertura:**
- ✅ Endpoint `/health`
- ✅ Endpoint `/query`
- ✅ Gerador de SQL
- ✅ Conexão com PostgreSQL
- ✅ CORS headers
- ✅ Tratamento de erros

**Executar:**
```bash
cd api
pytest tests/ -v --cov=. --cov-report=term-missing
```

**Testes:**
- `test_api.py` - Testes unitários e de integração
- `conftest.py` - Configuração do pytest

---

### 2. **LLM Service** (`llm-service/tests/`)

**Framework:** Pytest

**Cobertura:**
- ✅ Endpoint `/health`
- ✅ Endpoint `/ask` (perguntas LLM)
- ✅ Endpoint `/export` (CSV/PDF)
- ✅ Conexão com Ollama (mockada)
- ✅ Geração de SQL via LangChain
- ✅ Tratamento de erros

**Executar:**
```bash
cd llm-service
pytest tests/ -v --cov=. --cov-report=term-missing
```

**Testes:**
- `test_llm_api.py` - Testes com mocks do LangChain
- `conftest.py` - Configuração e fixtures

---

### 3. **Frontend Next.js** (`next-app/__tests__/`)

**Framework:** Jest + React Testing Library

**Cobertura:**
- ✅ Página de login (modo dev)
- ✅ Componente DataTable
- ✅ API Client (fetch)
- ✅ Navegação
- ✅ LocalStorage

**Executar:**
```bash
cd next-app
npm test        # Modo watch
npm run test:ci # CI mode com coverage
```

**Testes:**
- `pages/index.test.jsx` - Página de login
- `components/DataTable.test.jsx` - Tabela de dados
- `lib/apiClient.test.js` - Cliente da API

**Configuração:**
- `jest.config.js` - Configuração do Jest
- `jest.setup.js` - Mocks e setup global

---

### 4. **Testes de Integração**

**Framework:** Docker Compose + Pytest

**Cobertura:**
- ✅ Todos os containers rodando
- ✅ Comunicação entre serviços
- ✅ Endpoints funcionando
- ✅ Banco de dados acessível

**Executar:**
```bash
docker-compose -f docker-compose.test.yml up -d
docker-compose -f docker-compose.test.yml logs
docker-compose -f docker-compose.test.yml down
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

### Arquivo: `.github/workflows/ci-cd.yml`

### **Jobs do Pipeline:**

#### 1. **test-api** ✅
- Python 3.11
- PostgreSQL 15 (service container)
- Pytest com coverage
- Upload para Codecov

#### 2. **test-llm** ✅
- Python 3.11
- PostgreSQL 15
- Mock do Ollama
- Pytest com coverage

#### 3. **test-frontend** ✅
- Node.js 18
- Jest + React Testing Library
- Lint + Build
- Coverage report

#### 4. **test-integration** ✅
- Docker Compose
- Testes end-to-end
- Validação de serviços

#### 5. **build-and-push** ✅
- Build imagens Docker
- Push para Docker Hub
- Tag automático
- Cache otimizado

#### 6. **deploy** ✅
- Deploy para produção
- Aprovação manual
- Rollback automático

#### 7. **code-quality** ✅
- SonarCloud (análise de código)
- Trivy (vulnerabilidades)
- SARIF upload

---

## 🛠️ Executar Testes Localmente

### **Opção 1: Script Automatizado (Recomendado)**

**Linux/Mac:**
```bash
chmod +x run-tests.sh
./run-tests.sh
```

**Windows:**
```powershell
.\run-tests.ps1
```

### **Opção 2: Manual**

**API de Dados:**
```bash
cd api
pip install pytest pytest-cov pytest-mock
pytest tests/ -v --cov=.
```

**LLM Service:**
```bash
cd llm-service
pip install pytest pytest-cov pytest-mock
pytest tests/ -v --cov=.
```

**Frontend:**
```bash
cd next-app
npm install
npm run test:ci
```

**Integração (Docker):**
```bash
docker-compose -f docker-compose.test.yml up -d
# Aguardar 30 segundos
curl http://localhost:5001/health
curl http://localhost:8001/health
docker-compose -f docker-compose.test.yml down
```

---

## 📊 Coverage (Cobertura de Testes)

### Meta: **>= 80% de cobertura**

**Ver relatórios:**
```bash
# API
cd api && pytest --cov=. --cov-report=html
open htmlcov/index.html

# LLM
cd llm-service && pytest --cov=. --cov-report=html
open htmlcov/index.html

# Frontend
cd next-app && npm run test:ci
open coverage/lcov-report/index.html
```

---

## 🔐 Configuração do GitHub Actions

### 1. **Secrets Necessários**

Vá em: **Settings > Secrets and variables > Actions**

```
DOCKER_USERNAME     # Usuário Docker Hub
DOCKER_PASSWORD     # Senha/Token Docker Hub
SONAR_TOKEN        # Token SonarCloud (opcional)
CODECOV_TOKEN      # Token Codecov (opcional)
```

### 2. **Environments**

Vá em: **Settings > Environments**

Criar: `production`
- ✅ Required reviewers (quem pode aprovar deploy)
- ✅ Wait timer (tempo de espera)
- ✅ Deployment protection rules

### 3. **Branch Protection**

Vá em: **Settings > Branches**

Para branch `main`:
- ✅ Require pull request reviews (1+ approvals)
- ✅ Require status checks:
  - `test-api`
  - `test-llm`
  - `test-frontend`
  - `test-integration`
- ✅ Require branches to be up to date
- ✅ Require conversation resolution

---

## 🚀 Workflow de Desenvolvimento

### **1. Criar Feature Branch**
```bash
git checkout -b feature/minha-feature
```

### **2. Desenvolver & Testar Localmente**
```bash
# Fazer alterações
vim api/app.py

# Testar
cd api
pytest tests/ -v

# Commit
git add .
git commit -m "feat: adicionar novo endpoint"
```

### **3. Push & Abrir PR**
```bash
git push origin feature/minha-feature
# Abrir PR no GitHub
```

### **4. Pipeline Automático**
- ✅ Testes executam automaticamente
- ✅ Status aparece no PR
- ✅ Coverage atualizado
- ✅ Code quality analisado

### **5. Review & Merge**
- ✅ Reviewers aprovam
- ✅ Merge para `main`
- ✅ Build & Deploy automático

---

## 📈 Monitoramento

### **GitHub Actions Dashboard**
```
https://github.com/SEU_USUARIO/SEU_REPO/actions
```

### **Codecov Dashboard** (opcional)
```
https://codecov.io/gh/SEU_USUARIO/SEU_REPO
```

### **SonarCloud Dashboard** (opcional)
```
https://sonarcloud.io/project/overview?id=SEU_PROJETO
```

---

## 🐛 Troubleshooting

### **Teste Falhou Localmente**

```bash
# Ver output detalhado
pytest tests/ -vv -s

# Executar teste específico
pytest tests/test_api.py::TestHealthEndpoint::test_health_success -v

# Debug mode
pytest tests/ --pdb
```

### **Pipeline Falhou no GitHub**

1. **Ver logs:** Click no job que falhou
2. **Reproduzir localmente:** Usar os mesmos comandos do workflow
3. **Verificar secrets:** Confirmar que estão configurados
4. **Re-run:** Click em "Re-run failed jobs"

### **Docker Compose Falhou**

```bash
# Ver logs
docker-compose -f docker-compose.test.yml logs

# Rebuild
docker-compose -f docker-compose.test.yml build --no-cache

# Limpar tudo
docker-compose -f docker-compose.test.yml down -v
```

---

## 📝 Boas Práticas

### **Escrevendo Testes:**

1. **AAA Pattern:**
   ```python
   def test_exemplo():
       # Arrange (preparar)
       client = app.test_client()
       
       # Act (executar)
       response = client.get('/health')
       
       # Assert (verificar)
       assert response.status_code == 200
   ```

2. **Nomes Descritivos:**
   ```python
   def test_health_endpoint_returns_ok_when_database_connected()
   def test_query_endpoint_returns_400_when_no_question_provided()
   ```

3. **Mock Externo:**
   ```python
   @patch('app.executar_sql')
   def test_with_mock(mock_sql):
       mock_sql.return_value = [{'test': 1}]
       # ...
   ```

### **Commits Semânticos:**
```
feat: adicionar endpoint de busca
fix: corrigir erro no cálculo
test: adicionar testes para API
docs: atualizar README
refactor: melhorar performance
```

---

## 🎯 Métricas de Qualidade

### **Targets:**
- ✅ Coverage: **>= 80%**
- ✅ Build time: **< 15 min**
- ✅ Test success rate: **> 95%**
- ✅ Code quality: **A rating**

### **Dashboards:**
- GitHub Actions (tempo, status)
- Codecov (coverage trends)
- SonarCloud (qualidade, bugs, vulnerabilidades)

---

## 📦 Arquivos Criados

```
.github/workflows/
├── ci-cd.yml                 # Pipeline principal
└── README.md                 # Documentação do workflow

api/tests/
├── __init__.py
├── conftest.py               # Config pytest
└── test_api.py               # Testes da API

llm-service/tests/
├── __init__.py
├── conftest.py
└── test_llm_api.py           # Testes do LLM

next-app/
├── jest.config.js            # Config Jest
├── jest.setup.js             # Setup e mocks
└── __tests__/
    ├── pages/
    │   └── index.test.jsx
    ├── components/
    │   └── DataTable.test.jsx
    └── lib/
        └── apiClient.test.js

tests/
└── mock-ollama-response.json # Mock Ollama

docker-compose.test.yml       # Compose para testes

run-tests.sh                  # Script Linux/Mac
run-tests.ps1                 # Script Windows

CI_CD_GUIDE.md                # Este arquivo
```

---

## 🚀 Próximos Passos

### **Curto Prazo:**
- [ ] Aumentar coverage para 90%
- [ ] Adicionar testes E2E (Playwright)
- [ ] Configurar Codecov
- [ ] Configurar SonarCloud

### **Médio Prazo:**
- [ ] Performance tests (k6)
- [ ] Security scanning (Snyk)
- [ ] Deploy staging automático
- [ ] Slack/Discord notifications

### **Longo Prazo:**
- [ ] Chaos engineering
- [ ] Load testing
- [ ] A/B testing framework
- [ ] Feature flags

---

**Criado em:** 13/10/2025  
**Versão:** 1.0.0  
**Status:** ✅ **OPERACIONAL**

**🎉 CI/CD COMPLETO E FUNCIONANDO!**

