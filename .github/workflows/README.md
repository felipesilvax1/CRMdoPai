# 🔄 CI/CD Pipeline - GitHub Actions

## Visão Geral

Pipeline automatizado que executa em **cada push** e **pull request** para garantir a qualidade do código.

## Workflows

### `ci-cd.yml` - Pipeline Principal

**Triggers:**
- Push para `main` ou `develop`
- Pull Requests para `main` ou `develop`
- Dispatch manual

**Jobs:**

#### 1. **test-api** - Testes da API de Dados
- ✅ Python 3.11
- ✅ PostgreSQL 15 (service container)
- ✅ Pytest com coverage
- ✅ Upload para Codecov

#### 2. **test-llm** - Testes do LLM Service
- ✅ Python 3.11
- ✅ PostgreSQL 15 (service container)
- ✅ Mock do Ollama
- ✅ Pytest com coverage

#### 3. **test-frontend** - Testes do Frontend
- ✅ Node.js 18
- ✅ Jest + React Testing Library
- ✅ Lint
- ✅ Build de produção
- ✅ Coverage

#### 4. **test-integration** - Testes de Integração
- ✅ Docker Compose
- ✅ Testes end-to-end
- ✅ Validação de todos os serviços

#### 5. **build-and-push** - Build Docker Images
- ✅ Apenas em push para `main`
- ✅ Build e push para Docker Hub
- ✅ Versionamento automático
- ✅ Cache otimizado

#### 6. **deploy** - Deploy para Produção
- ✅ Apenas em push para `main`
- ✅ Ambiente de produção
- ✅ Aprovação manual (via GitHub Environments)

#### 7. **code-quality** - Análise de Código
- ✅ SonarCloud
- ✅ Trivy (vulnerabilidades)
- ✅ SARIF upload

## Configuração Necessária

### 1. Secrets do GitHub

Configure em: **Settings > Secrets and variables > Actions**

```
DOCKER_USERNAME      # Seu usuário do Docker Hub
DOCKER_PASSWORD      # Sua senha/token do Docker Hub
SONAR_TOKEN         # Token do SonarCloud (opcional)
CODECOV_TOKEN       # Token do Codecov (opcional)
```

### 2. Environments

Configure em: **Settings > Environments**

Crie o environment `production` com:
- ✅ Aprovação manual (reviewers)
- ✅ Deploy protection rules
- ✅ Secrets específicos de produção

### 3. Branch Protection

Configure em: **Settings > Branches > Branch protection rules**

Para `main`:
- ✅ Require pull request before merging
- ✅ Require status checks to pass before merging
  - `test-api`
  - `test-llm`
  - `test-frontend`
  - `test-integration`
- ✅ Require branches to be up to date

## Como Usar

### Desenvolvimento Normal

```bash
# 1. Criar branch
git checkout -b feature/minha-feature

# 2. Fazer alterações
# ... código ...

# 3. Commit
git add .
git commit -m "feat: minha nova feature"

# 4. Push
git push origin feature/minha-feature
```

**Pipeline automático irá:**
1. ✅ Executar todos os testes
2. ✅ Verificar qualidade do código
3. ✅ Reportar status no PR

### Deploy para Produção

```bash
# 1. Merge do PR para main
# (via GitHub UI após aprovação)

# 2. Pipeline automático irá:
#    - Rodar todos os testes
#    - Build das imagens Docker
#    - Push para Docker Hub
#    - Aguardar aprovação manual
#    - Deploy (se aprovado)
```

### Executar Workflow Manualmente

1. Vá em **Actions**
2. Selecione **CI/CD Pipeline**
3. Clique em **Run workflow**
4. Escolha a branch
5. Clique em **Run workflow**

## Status Badges

Adicione ao README.md:

```markdown
![CI/CD](https://github.com/SEU_USUARIO/SEU_REPO/workflows/CI%2FCD%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/SEU_USUARIO/SEU_REPO/branch/main/graph/badge.svg)
```

## Tempo de Execução Médio

| Job | Tempo | Paralelização |
|-----|-------|---------------|
| test-api | ~2-3 min | Sim |
| test-llm | ~2-3 min | Sim |
| test-frontend | ~2-3 min | Sim |
| test-integration | ~3-5 min | Após testes |
| build-and-push | ~5-7 min | Após testes |
| deploy | ~2-5 min | Após build |
| code-quality | ~1-2 min | Paralelo |

**Total (com paralelização):** ~10-15 minutos

## Troubleshooting

### Falha nos Testes

```bash
# Ver logs no GitHub Actions
# Ou executar localmente:
./run-tests.sh  # Linux/Mac
./run-tests.ps1 # Windows
```

### Falha no Build Docker

```bash
# Testar build local:
docker-compose -f docker-compose.test.yml build
```

### Falha no Deploy

1. Verificar secrets configurados
2. Verificar ambiente de produção
3. Revisar logs do workflow

## Otimizações

### Cache

O pipeline usa cache para:
- ✅ Dependências Python (pip)
- ✅ Dependências Node (npm)
- ✅ Layers Docker (buildx)

### Paralelização

Jobs executam em paralelo quando possível:
- test-api ∥ test-llm ∥ test-frontend ∥ code-quality
- test-integration (após testes)
- build-and-push (após testes)
- deploy (após build)

### Recursos

- ✅ Runners: ubuntu-latest (GitHub-hosted)
- ✅ Concorrência: Máx 4 jobs simultâneos (free tier)
- ✅ Timeout: 60 minutos por job

## Melhores Práticas

1. **Commits Semânticos:**
   ```
   feat: nova funcionalidade
   fix: correção de bug
   docs: documentação
   test: testes
   chore: manutenção
   ```

2. **Pull Requests:**
   - Nome descritivo
   - Descrição completa
   - Reviewers atribuídos
   - Labels apropriadas

3. **Testes:**
   - Escrever testes para novas features
   - Manter coverage acima de 80%
   - Testar localmente antes do push

4. **Deploy:**
   - Apenas via `main`
   - Aprovação obrigatória
   - Rollback plan definido

## Próximos Passos

- [ ] Adicionar testes E2E com Playwright
- [ ] Implementar deploy para Kubernetes
- [ ] Adicionar monitoring (Datadog/NewRelic)
- [ ] Implementar feature flags
- [ ] Adicionar performance tests (k6)

---

**Criado em:** 13/10/2025  
**Última atualização:** 13/10/2025

