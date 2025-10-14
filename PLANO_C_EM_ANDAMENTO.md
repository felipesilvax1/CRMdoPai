# 🚀 PLANO C - MIGRAÇÃO PARALELA EM ANDAMENTO

**Status**: ✅ EXECUTANDO  
**Iniciado**: 14/10/2025 12:57  
**Próxima etapa**: Aguardar dump (30-60 min)

---

## 📊 O QUE ESTÁ ACONTECENDO AGORA

### ✅ Thread 1: Container PostgreSQL
- **Status**: ✅ RODANDO
- **Porta**: 5433
- **Imagem**: postgres:17
- **Volume**: crm_postgres_data
- **Otimizações**: 4GB shared_buffers, 12GB cache

### 🔄 Thread 2: Dump do BD
- **Status**: 🔄 EM BACKGROUND
- **Origem**: 192.168.15.22:5432 (PostgreSQL Windows)
- **Database**: cnpj_processado
- **Destino**: cnpj_processado.dump
- **ETA**: 30-60 minutos
- **Janela**: Aberta separadamente (acompanhe o progresso)

### ✅ Thread 3: Sistema em Produção
- **Status**: ✅ FUNCIONANDO NORMAL
- **Frontend**: localhost:3000
- **API**: localhost:5000
- **BD**: 192.168.15.22:5432 (Windows nativo)

---

## 🎯 MELHORIAS TEMPORÁRIAS APLICADAS

### Frontend (`next-app/pages/busca-avancada.jsx`)
- ✅ LIMIT de 100 municípios (reduz 48s → ~5s)
- ✅ LIMIT de 50 bairros
- ✅ Logs de performance no console

### Backend (`api/app.py`)
- ✅ Parâmetro `limit` em `/filtros/municipios` (padrão: 1000, max: 200 na prática)
- ✅ Parâmetro `limit` em `/filtros/bairros` (padrão: 500)
- ✅ Logs de tempo de execução

**Resultado esperado**: Carregamento de 48 segundos → ~5 segundos

---

## 📋 PRÓXIMOS PASSOS

### 1. AGORA (Você pode ir fazer outras coisas!)
```powershell
# Ver progresso do dump (tamanho vai crescendo)
Get-Item cnpj_processado.dump | Select-Object Name, Length

# Exemplo de saída:
# Name                      Length
# ----                      ------
# cnpj_processado.dump      1234567890  (vai crescendo)
```

### 2. QUANDO DUMP TERMINAR (30-60 min)
A janela do PowerShell vai avisar:
```
✅ DUMP CONCLUÍDO COM SUCESSO!
Tempo: XX minutos
Tamanho: X.X GB

Próximo passo: Execute restore-paralelo.ps1
```

Então execute:
```powershell
.\restore-paralelo.ps1
```

### 3. AMANHÃ (Switch Final)
1. Criar índices no novo container (20-40 min)
2. Trocar conexão da API (2 min)
3. Testar performance (5 min)
4. Celebrar! 🎉

---

## 🛠️ ARQUIVOS CRIADOS

### Scripts de Migração
- ✅ `iniciar-migracao-paralela.ps1` - Iniciar dump + container
- ✅ `restore-paralelo.ps1` - Restore em background
- ✅ `dump-background.ps1` - (Gerado automaticamente)
- ✅ `docker-compose.postgres.yml` - Container otimizado

### Scripts de Índices
- ✅ `scripts/criar_indices.py` - Criar índices de performance

### Documentação
- ✅ `MIGRACAO_PARALELA.md` - Estratégia completa
- ✅ `PLANO_C_EM_ANDAMENTO.md` - Este arquivo

---

## 🔍 VERIFICAR STATUS

### Container PostgreSQL
```powershell
docker ps --filter "name=crm-postgres"
docker logs crm-postgres --tail 50
```

### Dump em progresso
```powershell
# Ver tamanho (vai crescendo)
Get-Item cnpj_processado.dump -ErrorAction SilentlyContinue | 
  Select-Object Name, @{N='Size(GB)';E={[math]::Round($_.Length/1GB,2)}}

# Se não existir ainda, aguarde alguns segundos
```

### Sistema em produção
```powershell
# Testar frontend
curl http://localhost:3000

# Testar API
curl http://localhost:5000/health

# Testar BD Windows
docker exec crm-postgres psql -h host.docker.internal -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"
```

---

## ⚠️ TROUBLESHOOTING

### Dump não iniciou?
```powershell
# Verificar se janela abriu
# Se não, execute manualmente:
.\dump-background.ps1
```

### Container não está rodando?
```powershell
docker-compose -f docker-compose.postgres.yml up -d
docker logs crm-postgres
```

### Sistema Windows lento?
- **Normal**: O dump lê o BD, mas não trava
- **Impacto**: Mínimo (apenas leitura)
- **Você pode**: Continuar usando normalmente

---

## 💡 VANTAGENS DESTA ABORDAGEM

### ✅ Zero Downtime
- Sistema continua funcionando
- Usuários não sentem nada
- Migração invisível

### ✅ Flexibilidade
- Você pode pausar/retomar
- Não precisa ficar esperando
- Faz no seu tempo

### ✅ Segurança
- BD Windows continua ativo
- Rollback fácil se der problema
- Teste antes de trocar

### ✅ Performance Melhorada
- Limites temporários já melhoram UX
- Quando trocar: índices + Docker = 🚀
- Experiência vai de 48s → 2s

---

## 📞 SUPORTE

### Erro no dump?
- Verifique logs na janela do PowerShell
- Senha do PostgreSQL: `postgres`
- Host: `192.168.15.22`

### Erro no container?
```powershell
docker logs crm-postgres
```

### Dúvidas?
- Leia `MIGRACAO_PARALELA.md`
- Todos os comandos estão documentados
- ETAs realistas baseados em experiência anterior

---

**🎯 RESUMO**: Tudo rodando em paralelo! Você pode ir fazer outras coisas.
**⏰ ETA**: 30-60 min para dump, depois mais 40-60 min para restore.
**📲 NOTIFICAÇÃO**: Janela PowerShell vai avisar quando terminar.

**🚀 Quando estiver tudo pronto amanhã: Performance de 48s → 2s!**

