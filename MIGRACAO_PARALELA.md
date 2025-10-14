# 🚀 MIGRAÇÃO PARALELA - Estratégia Zero Downtime

## 🎯 OBJETIVO
Migrar BD para Docker **EM PARALELO** enquanto sistema continua funcionando

---

## ⚡ ESTRATÉGIA (3 Fases Paralelas)

### FASE 1: AGORA (Paralelo - 30 min)
**Você continua usando o sistema normalmente!**

#### Thread 1: Solução Temporária (15 min) ✅
- Reduzir LIMIT de municípios (48s → 10s)
- Loading states melhores
- Sistema fica USÁVEL

#### Thread 2: Dump em Background (20-30 min) 🔄
```powershell
# Roda em paralelo, não afeta uso
pg_dump -h 192.168.15.22 -U postgres -Fc cnpj_processado -f cnpj_processado.dump
```
**Impacto**: Mínimo (apenas leitura do BD)

#### Thread 3: Preparar Container (2 min) ⚡
```powershell
# Criar container PostgreSQL VAZIO
docker-compose -f docker-compose.postgres.yml up -d
```

---

### FASE 2: BACKGROUND (40-60 min)
**Sistema Windows continua ativo! Você usa normalmente!**

```powershell
# Restore roda em background
docker exec -i crm-postgres pg_restore -U postgres -d cnpj_processado < cnpj_processado.dump
```

**Você pode**:
- ✅ Continuar usando o sistema
- ✅ Fazer outras coisas
- ✅ Ir dormir (roda sozinho)

---

### FASE 3: AMANHÃ (Switch Final - 60 min)
**Quando estiver pronto para o switch**

#### 1. Criar Índices no Novo BD (20-40 min)
```powershell
docker exec crm-postgres python /scripts/criar_indices.py
```

#### 2. Testar Novo Container (5 min)
```powershell
# Testar queries
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"
```

#### 3. Switch da API (2 min)
```yaml
# docker-compose.crm.yml
environment:
  - DB_HOST=crm-postgres  # ← Mudar de host.docker.internal
```

#### 4. Restart API (1 min)
```powershell
docker-compose -f docker-compose.crm.yml restart crm-api
```

#### 5. Validar (5 min)
- Testar filtros
- Verificar performance (2s ao invés de 48s!)
- Celebrar 🎉

---

## 📊 TIMELINE PARALELA

```
HOJE - 18:00
├─ [15 min] Implementar solução temporária
├─ [30 min] Dump BD (paralelo, você nem sente)
└─ [60 min] Restore (paralelo, você pode sair)

HOJE - 19:30
└─ Sistema funcionando + BD novo pronto em background!

AMANHÃ - Quando tiver tempo
├─ [40 min] Criar índices no novo BD
├─ [10 min] Testar + Switch
└─ [∞] Sistema 100% profissional! 🚀
```

---

## 🎯 VANTAGENS DESTA ABORDAGEM

### ✅ Você NÃO para de trabalhar
- Sistema continua rodando normal
- BD Windows continua ativo
- Zero downtime

### ✅ Migração roda sozinha
- Dump em background
- Restore em background
- Você pode ir fazer outras coisas

### ✅ Teste antes de trocar
- Novo BD fica pronto
- Você testa quando quiser
- Switch só quando estiver 100% confiante

### ✅ Rollback fácil
- Se algo der errado, sistema antigo continua lá
- Apenas aponta de volta para Windows
- Sem risco!

---

## 🛠️ SCRIPTS PRONTOS

### 1. Iniciar Migração Paralela AGORA
**Arquivo**: `iniciar-migracao-paralela.ps1`
**ETA**: 2 minutos para rodar, 30-60 min background
**Você pode**: Continuar trabalhando normalmente

### 2. Verificar Progresso
```powershell
# Ver tamanho do dump
Get-Item cnpj_processado.dump | Select-Object Name, @{N='Size(GB)';E={[math]::Round($_.Length/1GB,2)}}

# Ver se restore terminou
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"
```

### 3. Switch Final (amanhã)
**Arquivo**: `switch-para-docker.ps1`
**ETA**: 2 minutos
**Requisito**: Restore completo + índices criados

---

## 💡 RESPOSTA DIRETA

**SIM! Migração pode rodar em paralelo!**

**O QUE FAZER AGORA:**
1. Eu implemento solução temporária (15 min)
2. Inicio dump em background
3. Você continua usando o sistema normalmente
4. Amanhã: switch quando estiver pronto

**IMPACTO NO SEU TRABALHO**: ZERO
**TEMPO DEDICADO NECESSÁRIO**: 15 min agora + 10 min amanhã
**RESTO**: Roda sozinho em background

---

**Posso iniciar? Vai ser assim:**
1. ⚡ Reduzir LIMIT + loading states (15 min - você espera)
2. 🔄 Dump BD (30 min - roda sozinho, você nem sente)
3. 📦 Restore (60 min - roda sozinho, pode ir jantar)
4. 💤 Amanhã: índices + switch

**Confirma?** 🚀


