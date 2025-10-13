# ⏱️ Estimativa REALISTA de Migração

## 📊 Dados Medidos:

### Cenário Atual (WiFi):
- **Rede:** 7.1 MB/s
- **Método testado:** COPY texto (lento)
- **Taxa:** 455 registros/seg
- **Tempo:** 28 horas

---

## 🔌 Com Cabo Ethernet:

### Velocidade Real Esperada:
- **Rede teórica:** 1000 Mbps (Gigabit) = 125 MB/s
- **Rede prática:** ~80-100 MB/s (overhead de protocolo)
- **Melhoria:** 14x mais rápido que WiFi

### Mas... há outros fatores:

#### 1. **Método de Transferência:**

**COPY texto (que testamos):**
- ❌ Não comprime
- ❌ Processa linha por linha
- ❌ Single-thread
- ⏱️ 28h no WiFi → **2-3h no cabo**

**pg_dump -Fd (recomendado):**
- ✅ Formato binário (mais eficiente)
- ✅ Comprime automaticamente
- ✅ Paralelo (-j 8)
- ⏱️ Estimativa: **1-2h no cabo, 5-8h no WiFi**

#### 2. **Overhead PostgreSQL:**
- Serialização/deserialização: ~20% tempo
- Validação de constraints: ~10% tempo
- Criação de índices: ~15% tempo

#### 3. **Disk I/O:**
- Seu SSD: 117 MB/s ✓ (OK)
- PostgreSQL escrita: ~60-80 MB/s real
- Não é gargalo

---

## ✅ **RESPOSTA DIRETA:**

### Com Cabo Ethernet:

| Método | Workers | Tempo Estimado | Confiança |
|--------|---------|----------------|-----------|
| COPY texto | 1 | 2-3h | 90% |
| pg_dump -Fd | 4 | 2-3h | 80% |
| pg_dump -Fd | 8 | **1.5-2h** | 70% |
| pg_dump -Fd | 8 (otimizado*) | **1-1.5h** | 60% |

\* otimizado = sem índices durante import, criar depois

### Com WiFi (Atual):

| Método | Workers | Tempo Estimado |
|--------|---------|----------------|
| COPY texto | 1 | 24-28h |
| pg_dump -Fd | 4 | 8-12h |
| pg_dump -Fd | 8 | 5-8h |

---

## 🎯 **MELHOR ESTRATÉGIA:**

### Fase 1: Dump (no T14)
```bash
# Fazer dump DIRETO no T14 (não pela rede)
# Acessar o T14 remotamente ou fisicamente
docker exec c93d7f48cac6 pg_dump -U postgres -d cnpj_processed \
  -Fd -j 8 -f /backup/dump_cnpj/

# Tempo: ~20-30 minutos
```

### Fase 2: Copiar arquivo (via rede)
```powershell
# Copiar a pasta dump (15-25 GB comprimido)
# Via SMB/compartilhamento de rede
Copy-Item \\192.168.15.24\backup\dump_cnpj\ -Destination .\dump\ -Recurse

# Com cabo: ~3-5 minutos (25GB / 100MB/s = 250s)
# Com WiFi: ~45-60 minutos
```

### Fase 3: Restore (local)
```bash
docker exec cnpj_postgres_final pg_restore \
  -U postgres -d cnpj_processed \
  -j 8 -Fd /backup/dump_cnpj/

# Tempo: ~30-45 minutos
```

**TEMPO TOTAL COM CABO:**
- Dump: 25 min
- Cópia: 5 min
- Restore: 40 min
- **TOTAL: ~1-1.5 horas** ✅

**TEMPO TOTAL COM WiFi:**
- Dump: 25 min
- Cópia: 60 min
- Restore: 40 min
- **TOTAL: ~2 horas** (ainda viável!)

---

## 🔍 **VERIFICAÇÃO:**

A cópia de arquivo é **MUITO mais rápida** que streaming SQL:

| Método | Throughput |
|--------|------------|
| SQL via rede | 7 MB/s (WiFi) |
| Cópia de arquivo SMB | 40-50 MB/s (WiFi) |
| Cópia de arquivo Ethernet | 100-110 MB/s |

**Por quê?** Arquivo não tem overhead de PostgreSQL processando!

---

## ✅ **RESPOSTA FINAL:**

**Com cabo ethernet:**
- **Melhor caso:** 1 hora
- **Caso típico:** 1.5-2 horas
- **Pior caso:** 2.5 horas

**Com WiFi (se fizer dump + cópia de arquivo):**
- ~2 horas também! (método otimizado)

**Com WiFi (streaming direto):**
- 5-8 horas

---

## 🎯 **RECOMENDAÇÃO:**

1. **Esta noite:** Sistema funciona remotamente ✅
2. **Amanhã cedo:** 
   - Fazer dump no T14 (25 min)
   - Copiar arquivo via rede (5-60 min)
   - Restore local (40 min)
   - **Total: 1-2 horas** independente de cabo ou WiFi!

**O truque é fazer dump LOCALMENTE no T14 primeiro!** 🎯

