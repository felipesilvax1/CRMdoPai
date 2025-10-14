# 🎯 PLANO: Migração BD para Docker + Índices

## 📊 SITUAÇÃO ATUAL (Crítica)

### Problema de Performance
- **Query de municípios**: 48 segundos ⚠️
- **Causa**: 79M registros sem índices
- **Impacto UX**: INACEITÁVEL (usuário desiste)

### Arquitetura Atual
```
┌─────────────────────┐
│  PostgreSQL         │
│  (Windows nativo)   │ ← BD aqui (192.168.15.22:5432)
│  cnpj_processado    │
└─────────────────────┘
         ↑
         │ host.docker.internal
         │
┌─────────────────────┐
│  Docker Container   │
│  crm-api            │
└─────────────────────┘
```

**Problemas**:
- BD fora do Docker (difícil gerenciar)
- Backup/restore manual
- Não usa recursos do docker-compose
- Performance ruim sem índices

---

## 🎯 PLANO RECOMENDADO

### OPÇÃO A: Criar Índices Agora (Solução Rápida)
**ETA**: 20-40 minutos
**Prós**: 
- Resolve performance AGORA
- Municípios de 48s → 2s
**Contras**:
- BD continua fora do Docker
- Terá que refazer índices após migração

### OPÇÃO B: Migrar para Docker + Índices (Solução Completa) ✅ RECOMENDADO
**ETA**: 2-3 horas
**Fases**:

#### 1️⃣ Dump do BD (20-30 min)
```bash
pg_dump -h 192.168.15.22 -U postgres -Fc cnpj_processado > cnpj_processado.dump
```

#### 2️⃣ Criar Container PostgreSQL (5 min)
```yaml
# docker-compose.crm.yml
postgres:
  image: postgres:17
  container_name: crm-postgres
  volumes:
    - postgres_data:/var/lib/postgresql/data
  environment:
    POSTGRES_DB: cnpj_processado
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: password
  ports:
    - "5433:5432"  # Porta diferente para não conflitar
```

#### 3️⃣ Restore no Container (40-60 min)
```bash
docker exec -i crm-postgres pg_restore -U postgres -d cnpj_processado < cnpj_processado.dump
```

#### 4️⃣ Criar Índices (20-40 min)
- Rodar dentro do container
- Performance melhor
- Gerenciável

#### 5️⃣ Atualizar API (2 min)
```yaml
environment:
  - DB_HOST=crm-postgres  # ao invés de host.docker.internal
```

---

## 🚀 SOLUÇÃO TEMPORÁRIA (Para Hoje)

### Enquanto você decide:

1. **Implementar LIMIT mais agressivo**:
   - Reduzir de 50 → 20 municípios por UF
   - Adicionar paginação
   - **ETA**: 10 minutos
   - **Ganho**: 48s → 20s (ainda ruim, mas usável)

2. **Loading states melhores**:
   - Skeleton screens
   - Progress bars
   - **ETA**: 15 minutos
   - **Ganho**: UX tolerável

---

## ✅ RECOMENDAÇÃO FINAL

**PARA AMANHÃ**:
1. ✅ Commit do código atual (cache + otimizações)
2. ✅ Documentar estratégia
3. ⏰ **Agendar migração** para quando tiver 3-4h livres
4. ⚡ **Hoje**: Implementar loading states + reduzir LIMIT

**PRIORIDADE**:
```
Alta:    Loading states + LIMIT menor (resolve UX hoje)
Crítica: Migração BD → Docker (fazer quando tiver tempo)
Crítica: Criar índices (após migração)
```

---

## 📝 SCRIPTS PRONTOS

### Script de Migração (quando decidir)
**Arquivo**: `migrar-bd-para-docker.ps1`
**Tempo**: ~2-3 horas
**Requer**: Tempo dedicado + backup

---

## 💡 DECISÃO NECESSÁRIA

**Escolha uma**:
- [ ] **A**: Criar índices agora no BD Windows (20-40 min, solução parcial)
- [ ] **B**: Migrar tudo para Docker amanhã (3h, solução completa) ✅ RECOMENDADO
- [ ] **C**: Fazer solução temporária hoje (LIMIT + loading) e B amanhã ⚡ PRAGMÁTICO

---

**Data**: 14/10/2025
**Status**: Aguardando decisão do usuário

