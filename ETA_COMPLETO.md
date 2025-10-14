# ⏱️ ETA COMPLETO - Migração Automática

**Iniciado**: 14/10/2025 ~13:50  
**Script**: `executar-tudo-automatico.ps1`  
**Status**: 🔄 EM EXECUÇÃO AUTOMÁTICA

---

## 📊 TIMELINE DETALHADA

### ✅ CONCLUÍDO
```
13:06 - 13:31  Dump BD Windows          25 min  ✅
```

### 🔄 EM ANDAMENTO
```
13:50 - 14:40  Restore no Docker        50 min  🔄 (check a cada 3 min)
14:40 - 14:42  Validar Tabelas          2 min   ⏳
14:42 - 15:22  Criar Índices            40 min  ⏳
15:22 - 15:24  Switch da API            2 min   ⏳
15:24 - 15:27  Validar Performance      3 min   ⏳
```

**TOTAL**: ~1h 37min (até 15:27)

---

## 🔍 DETALHAMENTO POR ETAPA

### ETAPA 1: Restore (50 min) 🔄
**Início**: ~13:50  
**ETA**: 40-60 minutos  
**Término Estimado**: ~14:40  

**O que faz:**
- Importa 5.36 GB para container Docker
- Restaura ~77M+ registros
- Recria estrutura de tabelas

**Monitoramento:**
- Check a cada 3 minutos
- Conta registros em `estabelecimentos`
- Conclui quando > 70M registros

**Comando manual:**
```powershell
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"
```

---

### ETAPA 2: Validar Tabelas (2 min) ⏳
**Início**: Após restore  
**ETA**: 2 minutos  
**Término Estimado**: ~14:42  

**O que faz:**
- Verifica existência de tabelas auxiliares
- Valida: `municipios`, `cnaes`, `natureza_juridica`, `qualificacao_socio`
- Conta registros em cada tabela

**Por quê é importante:**
- Garante que municípios aparecem como NOMES (não códigos)
- Garante que CNAEs aparecem com descrição
- Essencial para UX

**Resultado esperado:**
```
✅ municipios: ~5,570 registros
✅ cnaes: ~1,300 registros
✅ natureza_juridica: ~80 registros
✅ qualificacao_socio: ~70 registros
```

---

### ETAPA 3: Criar Índices (30 min) ⏳
**Início**: Após validação  
**ETA**: 20-40 minutos  
**Término Estimado**: ~15:22  

**O que faz:**
- Cria 8 índices críticos de performance
- Usa `CREATE INDEX CONCURRENTLY` (não trava BD)
- Reporta progresso de cada índice

**Índices criados:**
1. `idx_estabelecimentos_uf_municipio` - Cascata UF→Município (crítico!)
2. `idx_estabelecimentos_uf` - Filtro por UF
3. `idx_estabelecimentos_municipio` - Filtro por Município  
4. `idx_estabelecimentos_bairro` - Filtro por Bairro
5. `idx_estabelecimentos_cnae` - Filtro por CNAE
6. `idx_estabelecimentos_situacao` - Filtro por Situação
7. `idx_estabelecimentos_cep` - Filtro por CEP
8. `idx_estabelecimentos_ddd` - Filtro por DDD

**Impacto esperado:**
```
ANTES:  48 segundos (sem índices)
DEPOIS:  2 segundos (com índices)
GANHO:  24x mais rápido! 🚀
```

---

### ETAPA 4: Switch da API (2 min) ⏳
**Início**: Após índices  
**ETA**: 2 minutos  
**Término Estimado**: ~15:24  

**O que faz:**
1. Atualiza `docker-compose.crm.yml`:
   ```yaml
   DB_HOST=crm-postgres  # era: host.docker.internal
   ```
2. Conecta container na rede
3. Reinicia API
4. Testa conexão

**Rollback (se necessário):**
```powershell
# Restaurar backup
cp docker-compose.crm.yml.bak docker-compose.crm.yml
docker-compose -f docker-compose.crm.yml restart crm-api
```

---

## 📈 PROGRESSO EM TEMPO REAL

### Como Acompanhar

**Ver progresso do restore:**
```powershell
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"
```

**Ver criação de índices:**
```powershell
# Indices existentes
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT indexname FROM pg_indexes WHERE tablename = 'estabelecimentos'"

# Progresso de criação (se suportado)
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT * FROM pg_stat_progress_create_index"
```

**Ver saúde da API:**
```powershell
curl http://localhost:5000/health
```

---

## ⏰ ESTIMATIVAS DE CONCLUSÃO

**Cenário Rápido** (tudo ideal):
```
Restore:  40 min → Conclusão: 14:30
Validar:   2 min → Conclusão: 14:32
Índices:  20 min → Conclusão: 14:52
Switch:    2 min → Conclusão: 14:54
TOTAL: 1h 04min
```

**Cenário Médio** (esperado):
```
Restore:  50 min → Conclusão: 14:40
Validar:   2 min → Conclusão: 14:42
Índices:  30 min → Conclusão: 15:12
Switch:    2 min → Conclusão: 15:14
TOTAL: 1h 24min
```

**Cenário Lento** (pessimista):
```
Restore:  60 min → Conclusão: 14:50
Validar:   2 min → Conclusão: 14:52
Índices:  40 min → Conclusão: 15:32
Switch:    2 min → Conclusão: 15:34
TOTAL: 1h 44min
```

---

## 🎯 RESULTADO FINAL ESPERADO

### Performance
```
Carregar municípios de SP:
  ANTES:      48 segundos
  TEMPORÁRIO:  5 segundos (com LIMIT)
  FINAL:       2 segundos (com índices)

Carregar bairros de São Paulo:
  ANTES:      30 segundos
  TEMPORÁRIO:  3 segundos (com LIMIT)
  FINAL:       1 segundo (com índices)
```

### Arquitetura
```
Cliente
  ↓
Nginx (porta 80) - Opcional
  ↓
Next.js (porta 3000)
  ↓
API Flask (porta 5000)
  ↓
PostgreSQL Docker (crm-postgres) ✨ NOVO!
  ├─ 77M+ registros
  ├─ 8 índices de performance
  ├─ Tabelas auxiliares validadas
  └─ Otimizado para 4GB RAM
```

---

## 💡 DURANTE A EXECUÇÃO

### Você PODE:
- ✅ Continuar usando o sistema
- ✅ Ir fazer outras coisas
- ✅ Fechar este terminal
- ✅ Script roda sozinho!

### Você VAI VER:
- 📊 Progresso a cada 3 minutos
- 📊 ETA atualizado
- 📊 Etapas concluídas
- 📊 Resultado final

---

## 📞 NOTIFICAÇÕES

O script vai mostrar:

```
[1/25] Tempo decorrido: 3.0 min
  Aguardando container responder...
  Próxima verificação em 3 minutos...

[2/25] Tempo decorrido: 6.0 min
  Registros importados: 5,234,567
  Próxima verificação em 3 minutos...

...

[15/25] Tempo decorrido: 45.0 min
  Registros importados: 77,123,456
  ✅ RESTORE CONCLUÍDO!
  
[ETAPA 2/4] Validando Tabelas Auxiliares
  ✅ municipios: 5,570 registros
  ✅ cnaes: 1,358 registros
  
[ETAPA 3/4] Criando Índices de Performance
  [1/8] idx_estabelecimentos_uf_municipio
    ✅ Criado em 234.5s
  ...
  
[ETAPA 4/4] Switch da API
  ✅ API conectada ao novo BD!
  
✅ MIGRAÇÃO COMPLETA!
```

---

## 🛠️ COMANDOS DE ACOMPANHAMENTO

### Ver Progresso do Script
```powershell
# Ver janela de execução (se fechou)
# Não pode recuperar, mas pode verificar status:

# Ver registros no BD
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"

# Ver índices criados
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT indexname FROM pg_indexes WHERE tablename = 'estabelecimentos'"
```

### Verificar Sistema
```powershell
# API funcionando?
curl http://localhost:5000/health

# Testar performance
curl "http://localhost:5000/filtros/municipios?uf=SP&limit=10"
```

---

**🚀 Script executando automaticamente!**  
**⏰ ETA total: 1-2 horas**  
**💤 Você pode ir fazer outras coisas!**

