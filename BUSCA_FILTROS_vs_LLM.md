# 💡 Busca com Filtros vs Chat LLM

## 🎯 Sistema Híbrido Implementado

Agora você tem **2 formas de buscar** dados:

```
┌────────────────────────────────────────────┐
│  🔍 BUSCA AVANÇADA (Filtros)              │
│  • Grátis                                  │
│  • Instantânea                             │
│  • Filtros visuais (tipo Excel)           │
│  • Ideal para: buscas simples              │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  🤖 CHAT LLM (IA)                          │
│  • Usa GPU (custo)                         │
│  • 10-30 segundos por pergunta             │
│  • Linguagem natural                       │
│  • Ideal para: queries complexas           │
└────────────────────────────────────────────┘
```

---

## 🔍 BUSCA AVANÇADA (Recomendado para 90% dos casos)

### **Página:** http://localhost:3000/busca-avancada

### **Filtros Disponíveis:**

1. **Estado (UF)** - Dropdown com contagem
   - Exemplo: SP (22.873.914 estabelecimentos)

2. **Município** - Autocomplete
   - Digite para buscar
   - Exemplo: "Barueri"

3. **Situação Cadastral** - Dropdown
   - ✅ Ativa (02)
   - ⚪ Nula (01)
   - ⏸️ Suspensa (03)
   - ❌ Inapta (04)
   - 🔻 Baixada (08)

4. **Limite de Resultados**
   - 10, 50, 100, 500, 1000

### **Vantagens:**
- ✅ **Grátis** (sem custo de IA)
- ✅ **Instantâneo** (< 1 segundo)
- ✅ **Fácil** (clica e seleciona)
- ✅ **Previsível** (vê o que está filtrando)
- ✅ **Econômico** para produção

### **Quando Usar:**
- ✅ "Quero empresas de SP"
- ✅ "Empresas ativas em Barueri"
- ✅ "Estabelecimentos em MG"
- ✅ Qualquer busca com 1-3 filtros simples

---

## 🤖 CHAT LLM (Para Queries Complexas)

### **Página:** http://localhost:3000/chat-llm

### **Capacidades:**

1. **Linguagem Natural**
   - "Quantos estabelecimentos ativos no Brasil?"
   - "Empresas em Barueri SP"
   
2. **Queries Complexas**
   - "Top 10 cidades com mais empresas"
   - "CNAEs mais comuns em MG"
   - "Distribuição por estado"
   - JOINs automáticos

3. **Análises**
   - Agregações (COUNT, GROUP BY)
   - Ordenações complexas
   - Múltiplos filtros

### **Desvantagens:**
- ⚠️ **Custo** (usa GPU)
- ⚠️ **Lento** (10-30 segundos)
- ⚠️ **Primeira vez** (~2 minutos)
- ⚠️ **Pode errar** o SQL (raras vezes)

### **Quando Usar:**
- ✅ Queries que precisam de JOIN
- ✅ Análises estatísticas
- ✅ Perguntas em linguagem natural
- ✅ Queries que você não sabe fazer

---

## 📊 COMPARAÇÃO

| Feature | Busca Avançada | Chat LLM |
|---------|----------------|----------|
| **Custo** | 💚 Grátis | 💰 GPU (caro) |
| **Velocidade** | ⚡ < 1s | 🐢 10-30s |
| **Facilidade** | 😊 Muito fácil | 🤔 Natural |
| **Precisão** | ✅ 100% | ✅ ~95% |
| **Filtros** | 4 principais | ∞ ilimitado |
| **Queries** | Simples | Complexas |
| **Exports** | ❌ Não | ✅ CSV/PDF |
| **JOINs** | ❌ Não | ✅ Sim |

---

## 💰 ECONOMIA EM PRODUÇÃO

### **Cenário 1: Só LLM**
```
1000 usuários/dia × 10 queries/usuário = 10.000 queries/dia
10.000 queries × 30s GPU = 83 horas de GPU/dia
Custo estimado: $$$$ 💸
```

### **Cenário 2: Híbrido (90% Filtros + 10% LLM)**
```
90% queries simples → Busca Avançada (grátis)
10% queries complexas → Chat LLM (GPU)

10.000 queries/dia:
  - 9.000 via filtros = GRÁTIS ✅
  - 1.000 via LLM = 8,3h GPU/dia
  
Custo estimado: $ (90% de economia!) 💰
```

---

## 🎯 FLUXO RECOMENDADO

```
Usuário quer buscar
        ↓
    ┌───────┐
    │Simples?│
    └───┬───┘
        │
    ┌───┴───┐
   SIM     NÃO
    │       │
    ↓       ↓
┌────────┐ ┌──────┐
│Filtros │ │ LLM  │
│Grátis  │ │ IA   │
└────────┘ └──────┘
```

### **Queries Simples (Filtros):**
- Buscar por UF
- Buscar por município
- Filtrar por situação
- Limitar resultados

### **Queries Complexas (LLM):**
- "Top 10 cidades com mais empresas"
- "CNAEs mais comuns por estado"
- "Distribuição geográfica"
- Qualquer coisa com GROUP BY ou JOINs

---

## 🚀 COMO USAR

### **1. Abra a Busca Avançada:**
```
http://localhost:3000/busca-avancada
```

### **2. Selecione Filtros:**
- Estado: **SP**
- Município: **Barueri** (autocomplete)
- Situação: **Ativa**
- Limite: **50**

### **3. Clique "Buscar":**
- ⚡ Resultado em < 1 segundo
- 📊 Mostra total encontrado
- 📋 Tabela com dados

### **4. Se precisar de algo complexo:**
- Clique em **"🤖 Usar IA (LLM)"**
- Redireciona para o Chat
- Faça pergunta em português

---

## 📝 EXEMPLOS PRÁTICOS

### **Use Filtros Para:**

```
✅ "Empresas de SP"
   → Filtro: UF = SP

✅ "Empresas ativas em Barueri"
   → Filtro: UF = SP + Município = Barueri + Situação = Ativa

✅ "Estabelecimentos ativos no Brasil"
   → Filtro: Situação = Ativa (sem UF)

✅ "Ver 100 empresas de MG"
   → Filtro: UF = MG + Limite = 100
```

**Tempo:** < 1 segundo cada ⚡  
**Custo:** $0 💚

### **Use LLM Para:**

```
✅ "Quais as 10 cidades com mais empresas?"
   → Requer: GROUP BY município + ORDER BY count DESC

✅ "CNAEs mais comuns em cada estado"
   → Requer: GROUP BY uf, cnae

✅ "Empresas de tecnologia em SP"
   → Requer: Interpretação de "tecnologia" + filtro CNAE

✅ "Distribuição de empresas ativas por região"
   → Requer: Análise complexa
```

**Tempo:** 10-30 segundos cada 🐢  
**Custo:** GPU 💰

---

## 🎯 ENDPOINTS DA API

### **Novos Endpoints (Filtros):**

```bash
GET  /filtros/ufs
GET  /filtros/municipios?uf=SP&busca=Barueri
GET  /filtros/cnaes
POST /query/filtrado
```

### **Exemplo de Query Filtrada:**

```javascript
POST http://localhost:5000/query/filtrado
{
  "uf": "SP",
  "municipio": "6291",
  "situacao": "02",
  "limit": 100
}

// Resposta:
{
  "dados": [...],
  "total_encontrado": 622956,
  "total_retornado": 100,
  "filtros_aplicados": {...}
}
```

---

## 📊 ESTATÍSTICAS

### **Dados do Banco:**
- **Total:** 79.225.899 estabelecimentos
- **Ativos:** 31.385.313 (40%)
- **São Paulo:** 22.873.914 (29%)
- **Barueri (SP):** 622.956

### **Performance:**
- **Filtros:** < 1 segundo
- **LLM:** 10-30 segundos
- **Economia:** 90% quando usa filtros

---

## 🎉 BENEFÍCIOS DO SISTEMA HÍBRIDO

### **Para o Usuário:**
- ✅ Escolha a melhor ferramenta
- ✅ Filtros para buscas rápidas
- ✅ LLM para análises complexas
- ✅ Interface intuitiva

### **Para a Empresa:**
- ✅ 90% de economia em GPU
- ✅ Resposta instantânea
- ✅ Escalabilidade
- ✅ Melhor UX

### **Para o Sistema:**
- ✅ Menos carga no Ollama
- ✅ Queries SQL diretas (otimizadas)
- ✅ Cache possível nos filtros
- ✅ Monitoramento mais fácil

---

## 🚀 PRÓXIMAS MELHORIAS

- [ ] Cache Redis para filtros
- [ ] Exportação CSV nos filtros
- [ ] Filtro por CNAE (com descrição)
- [ ] Histórico de buscas
- [ ] Salvar filtros favoritos

---

**Criado em:** 13/10/2025  
**Versão:** 2.0  
**Status:** ✅ **IMPLEMENTADO E TESTADO**

**💡 Use Filtros primeiro, LLM depois!**

