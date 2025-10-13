# 🎯 Recomendação de Workers para pg_dump

## ⚠️ **IMPORTANTE: Não Use Todos os Cores!**

### Cálculo Seguro:

**Fórmula:**
```
Workers = MIN(
    Cores * 0.5,           # 50% dos cores
    (RAM_GB - 8) / 0.2     # RAM disponível considerando overhead
)
```

### 📊 Cenários por RAM:

| RAM Total | RAM Livre | Workers Seguros | Comando |
|-----------|-----------|-----------------|---------|
| 16 GB | ~8 GB | **4** | `-j 4` |
| 32 GB | ~16 GB | **6** | `-j 6` |
| 64 GB | ~32 GB | **8** | `-j 8` |
| 128 GB | ~64 GB | **12** | `-j 12` |

### 💾 Consumo de Memória:

**Por Worker:**
- pg_dump worker: ~200 MB
- Buffer PostgreSQL: ~100 MB
- Sistema operacional: ~300 MB
- **Total por worker: ~600 MB**

**Exemplo com 6 workers:**
- 6 workers × 600 MB = **3.6 GB**
- Docker overhead: **2 GB**
- Sistema + Chrome/apps: **4 GB**
- **Total necessário: ~10 GB**

---

## ⚡ **Recomendação CONSERVADORA:**

### Para Xeon com RAM < 32GB:
```bash
# Use 4 workers (seguro)
docker run --rm -e PGPASSWORD=password \
  -v ${PWD}/dump:/dump \
  postgres:15 pg_dump \
  -h 192.168.15.24 -U postgres -d cnpj_processed \
  -Fd -j 4 -f /dump/cnpj_parallel/

# Tempo estimado: 40-60 minutos
```

### Para Xeon com RAM 32-64GB:
```bash
# Use 6 workers (ótimo custo-benefício)
docker run --rm -e PGPASSWORD=password \
  -v ${PWD}/dump:/dump \
  postgres:15 pg_dump \
  -h 192.168.15.24 -U postgres -d cnpj_processed \
  -Fd -j 6 -f /dump/cnpj_parallel/

# Tempo estimado: 25-40 minutos
```

### Para Xeon com RAM > 64GB:
```bash
# Use 8-10 workers (performance máxima)
docker run --rm -e PGPASSWORD=password \
  -v ${PWD}/dump:/dump \
  postgres:15 pg_dump \
  -h 192.168.15.24 -U postgres -d cnpj_processed \
  -Fd -j 8 -f /dump/cnpj_parallel/

# Tempo estimado: 15-25 minutos
```

---

## 🚨 Sinais de RAM Insuficiente:

### Durante a migração, monitore:

```powershell
# Abrir Task Manager e observar:
# 1. Memory: uso não deve passar de 85%
# 2. Disk: se atividade alta mas RAM baixa = SWAP/Page File ativo (RUIM!)
# 3. CPU: deve estar consistente entre 40-60%
```

**Se ver Page File sendo usado:**
- ❌ PARE o processo (Ctrl+C)
- Reduza workers: `-j 4` → `-j 2`
- Tente novamente

---

## 💡 Alternativa: Migração Sequencial (Mais Lenta, Mais Segura)

Se RAM for crítica, migre **tabela por tabela**:

```bash
# 1. Tabelas pequenas primeiro (rápido)
for table in cnaes municipios naturezas qualificacoes paises motivos; do
  echo "Migrando $table..."
  docker run --rm -e PGPASSWORD=password postgres:15 \
    pg_dump -h 192.168.15.24 -U postgres -d cnpj_processed \
    -t $table | docker exec -i cnpj_postgres_final \
    psql -U postgres -d cnpj_processed
done

# 2. Tabelas médias (simples)
docker run --rm -e PGPASSWORD=password postgres:15 \
  pg_dump -h 192.168.15.24 -U postgres -d cnpj_processed \
  -t simples -Fc | docker exec -i cnpj_postgres_final \
  pg_restore -U postgres -d cnpj_processed

# 3. Tabelas grandes COM paralelização moderada
# Socios (26M registros)
docker run --rm -e PGPASSWORD=password postgres:15 \
  pg_dump -h 192.168.15.24 -U postgres -d cnpj_processed \
  -t socios -Fd -j 4 -f /dump/socios/

docker exec cnpj_postgres_final \
  pg_restore -U postgres -d cnpj_processed \
  -j 4 -Fd /dump/socios/

# Empresas (77M registros) - DIVIDIR EM LOTES
# Exportar em chunks de 10M
for i in {0..7}; do
  offset=$((i * 10000000))
  docker run --rm -e PGPASSWORD=password postgres:15 \
    psql -h 192.168.15.24 -U postgres -d cnpj_processed \
    -c "COPY (SELECT * FROM empresas LIMIT 10000000 OFFSET $offset) TO STDOUT" \
    | docker exec -i cnpj_postgres_final \
    psql -U postgres -d cnpj_processed \
    -c "COPY empresas FROM STDIN"
  echo "Chunk $i concluído (${offset} registros)"
done

# Estabelecimentos (79M registros) - igual empresas
```

**Vantagens:**
- Usa apenas ~1-2 GB RAM
- Pode pausar e continuar depois
- Progresso visível por tabela
- Mais lento: 2-4 horas total

---

## 🎓 **Regra de Ouro:**

```
Workers = (Cores_Disponiveis / 2) OU (RAM_GB / 5)
                 O QUE FOR MENOR!
```

**Exemplo:**
- 12 cores, 32 GB RAM
- Opção 1: 12 / 2 = **6 workers**
- Opção 2: 32 / 5 = **6.4 workers**
- **Resultado: Use 6 workers** ✓

---

## 🔍 Como Descobrir sua RAM:

```powershell
# No PowerShell:
Get-WmiObject Win32_PhysicalMemory | 
  Measure-Object Capacity -Sum | 
  Select-Object @{N="RAM_GB";E={[math]::round($_.Sum/1GB)}}

# No Task Manager:
# Performance → Memory → olhe "Total"
```

---

## ✅ Checklist Pré-Migração:

- [ ] Fechar Chrome/navegadores (libera ~2-4 GB)
- [ ] Fechar aplicações pesadas (IDE, etc)
- [ ] Verificar RAM livre > 8 GB
- [ ] Espaço em disco > 30 GB livre
- [ ] Testar com tabela pequena primeiro
- [ ] Monitorar Task Manager durante processo

---

**Atualizado:** 13/10/2025 00:15  
**Recomendação padrão:** `-j 4` ou `-j 6` (seguro para maioria dos casos)


