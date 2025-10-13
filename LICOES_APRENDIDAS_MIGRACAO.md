# 📝 Lições Aprendidas - Migração PostgreSQL

**Data:** 12/10/2025  
**Tarefa:** Migrar 77M+ registros do PostgreSQL (T14: 192.168.15.24) para PostgreSQL local

---

## ❌ Problemas Encontrados

### 1. **pg_dump travando em single-thread**
**Sintoma:** Processo consumia 1 core do Xeon, ignorando os outros 11 cores  
**Causa:** `pg_dump` padrão não usa paralelização  
**Impacto:** Estimativa de 2-3 horas só para fazer o dump

**Tentativas:**
```bash
# Comando que travou:
docker run --rm -e PGPASSWORD=password postgres:15 pg_dump \
  -h 192.168.15.24 -U postgres -d cnpj_processed \
  -Fc -f dump.backup
```

### 2. **Script Python com input() em ambiente não-interativo**
**Sintoma:** `EOFError: EOF when reading a line`  
**Causa:** Scripts rodando via `run_terminal_cmd` não têm stdin  
**Solução:** Remover todos os `input()` dos scripts

### 3. **Encoding Windows (cp1252) vs UTF-8**
**Sintoma:** Emojis e caracteres especiais quebravam  
**Exemplo:** `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680'`  
**Solução:** Usar apenas ASCII nos prints

### 4. **PowerShell: problema com tabelas hash**
**Sintoma:** `Measure-Object : The property "Peso" cannot be found`  
**Causa:** Sintaxe de hashtable no PowerShell não foi reconhecida corretamente  
**Código problemático:**
```powershell
$tabelas = @(
    @{Nome="empresas"; Registros=77041156; Peso=35}
)
```

### 5. **Comandos interrompidos pelo usuário**
**Causa:** Processos demorando muito sem feedback de progresso  
**Problema:** Falta de ETA e barra de progresso em tempo real

---

## ✅ O Que Funcionou

### 1. **Conexão Direta via Rede**
```python
# API conectando diretamente ao PostgreSQL remoto
DB_CONFIG = {
    'host': '192.168.15.24',
    'port': 5432,
    'database': 'cnpj_processed',
    'user': 'postgres',
    'password': 'password'
}
```
- ✅ Funciona instantaneamente
- ✅ Zero migração necessária
- ❌ Depende do T14 estar ligado

### 2. **Docker Compose com variáveis de ambiente**
```yaml
services:
  api:
    environment:
      - DB_HOST=192.168.15.24
      - DB_PORT=5432
      - USE_POSTGRES=true
```
- ✅ Fácil alternar entre SQLite e PostgreSQL
- ✅ Configurável sem rebuild

### 3. **Teste de conectividade funcionou**
```powershell
Test-NetConnection -ComputerName 192.168.15.24 -Port 5432
# TcpTestSucceeded : True ✓
```

---

## 🎯 Soluções para Amanhã

### Opção 1: Dump Paralelo (RECOMENDADO)
```bash
# Usar pg_dump com paralelização
pg_dump -h 192.168.15.24 -U postgres -d cnpj_processed \
  -Fd -j 12 -f /backup/dump_dir/

# -Fd = formato directory (permite paralelização)
# -j 12 = usar 12 jobs paralelos (1 por core do Xeon)
```

**Vantagens:**
- Usa todos os cores do Xeon
- Dump em 15-30 minutos (estimado)
- Restore também paralelo com `pg_restore -j 12`

**Comando completo:**
```bash
# 1. Dump paralelo
docker run --rm -e PGPASSWORD=password \
  -v ${PWD}/dump:/dump \
  postgres:15 pg_dump \
  -h 192.168.15.24 -U postgres -d cnpj_processed \
  -Fd -j 12 -f /dump/cnpj_parallel/

# 2. Restore paralelo
docker exec cnpj_postgres_final pg_restore \
  -U postgres -d cnpj_processed \
  -j 12 -Fd /dump/cnpj_parallel/
```

### Opção 2: COPY Direto (Mais Rápido)
```sql
-- Para cada tabela grande, fazer COPY direto
-- Origem (T14):
COPY empresas TO STDOUT WITH (FORMAT BINARY)

-- Destino (Local):  
COPY empresas FROM STDIN WITH (FORMAT BINARY)
```

**Vantagens:**
- Método mais rápido do PostgreSQL
- Formato binário = menos overhead
- Pode rodar múltiplas tabelas em paralelo

### Opção 3: Streaming via pipe (MÁXIMA VELOCIDADE)
```bash
# Dump e restore ao mesmo tempo via pipe
docker run --rm -e PGPASSWORD=password postgres:15 \
  pg_dump -h 192.168.15.24 -U postgres cnpj_processed \
  | docker exec -i cnpj_postgres_final \
  psql -U postgres -d cnpj_processed

# Comprimido (mais lento mas economiza banda):
pg_dump ... | gzip | gunzip | psql ...
```

---

## 📊 Dados do Banco

**PostgreSQL Remoto (T14 - 192.168.15.24):**
- **Banco:** `cnpj_processed`
- **User:** `postgres`
- **Password:** `password`
- **Porta:** `5432`

**Tabelas e Tamanhos:**
| Tabela | Registros | Prioridade |
|--------|-----------|------------|
| estabelecimentos | 79.225.899 | ALTA |
| empresas | 77.041.156 | ALTA |
| socios | 26.197.302 | MÉDIA |
| simples | ~1.000.000 | BAIXA |
| cnaes | 2.718 | BAIXA |
| municipios | 5.570 | BAIXA |
| naturezas | ~100 | BAIXA |
| qualificacoes | ~100 | BAIXA |
| motivos | ~100 | BAIXA |
| paises | ~200 | BAIXA |

**Total estimado:** ~182 milhões de registros

---

## 🔧 Status Atual do Sistema

### ✅ Funcionando:
- Frontend Docker: `http://localhost:3000`
- API Docker: `http://localhost:5000`
- API conectada ao PostgreSQL remoto via rede
- Health check funcionando

### ⚠️ Pendente:
- Migração completa dos dados para local
- Validação de integridade (checksum)
- Comparação com SQLite original

### 📁 Arquivos Criados:
- `docker-compose.yml` - Orquestração completa
- `api/app.py` - API com suporte PostgreSQL E SQLite
- `api/Dockerfile` - Container otimizado
- `importar_paralelo.py` - Script de migração paralela (incompleto)
- `importar_com_progresso.ps1` - Script PowerShell com ETA (tem bugs)
- `ARQUITETURA.md` - Documentação do sistema

---

## 💡 Recomendação para Amanhã

**PLANO A - Rápido (30-60 min):**
1. Usar `pg_dump -Fd -j 4` ou `-j 6` (NÃO 12! veja RECOMENDACAO_WORKERS.md)
2. Criar diretório local para receber
3. Fazer restore com `pg_restore -j 4` ou `-j 6`
4. Validar com checksums
5. Atualizar API para usar banco local

⚠️ **IMPORTANTE:** Usar todos os 12 cores pode esgotar RAM e causar swap!

**PLANO B - Se PLANO A falhar:**
1. Manter conexão remota
2. Configurar VPN ou túnel SSH persistente
3. Otimizar queries na API
4. Implementar cache local

**PLANO C - Híbrido:**
1. Migrar apenas tabelas principais (empresas, estabelecimentos)
2. Deixar tabelas pequenas (cnaes, municipios) acessíveis via remote
3. API com lógica híbrida

---

## 🐛 Bugs a Corrigir

1. **importar_paralelo.py:**
   - Linha 215: Remover `input()`
   - Linha 119: `os.path.getsize()` pode falhar no Windows
   - Adicionar tratamento de erros em `copiar_tabela_direta()`

2. **importar_com_progresso.ps1:**
   - Linha 23: Sintaxe de hashtable quebrada
   - Encoding de caracteres especiais
   - Progress bar não atualiza corretamente

3. **api/app.py:**
   - Adicionar connection pooling para performance
   - Implementar retry logic para falhas de rede
   - Cache de queries frequentes

---

## 📝 Notas Técnicas

### Estimativas de Tempo:
- **pg_dump single-thread:** 2-3 horas
- **pg_dump -j 12:** 15-30 minutos
- **COPY direto:** 10-20 minutos
- **Streaming pipe:** 20-40 minutos

### Largura de Banda:
- Rede local (Gigabit): ~100-120 MB/s teórico
- Overhead PostgreSQL: ~40-60 MB/s real
- Tamanho estimado dump: 15-25 GB comprimido

### Hardware:
- **PC Atual:** Xeon (12 cores disponíveis)
- **T14 Remoto:** IP 192.168.15.24, PostgreSQL na porta 5432
- **Rede:** Local, latência ~1ms

---

## ✅ Checklist para Amanhã

- [ ] Testar pg_dump com -Fd -j 12
- [ ] Criar diretório para dump paralelo
- [ ] Monitorar progresso em tempo real
- [ ] Validar integridade pós-migração
- [ ] Comparar com SQLite original
- [ ] Atualizar docker-compose.yml para usar banco local
- [ ] Testar performance das queries
- [ ] Criar índices no PostgreSQL local
- [ ] Documentar comandos finais
- [ ] Backup do banco local

---

**Última atualização:** 12/10/2025 23:00  
**Próxima sessão:** 13/10/2025

