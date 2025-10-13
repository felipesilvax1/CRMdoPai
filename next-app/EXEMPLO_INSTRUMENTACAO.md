# 📊 Exemplo de Instrumentação com Métricas

Este documento mostra como adicionar métricas Prometheus nas suas páginas e API routes.

---

## 🎯 Caso de Uso: Página de Busca Avançada

### **Antes (sem métricas):**

```typescript
// pages/busca-avancada.jsx
const handleBuscar = async () => {
  setBuscando(true);
  setDados([]);

  try {
    const response = await fetch(`${API_URL}/query/filtrado`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uf: ufSelecionada || null,
        municipio: municipioSelecionado || null,
        situacao: situacaoSelecionada || null,
        limit: limiteSelecionado
      })
    });

    const data = await response.json();
    
    if (data.dados) {
      setDados(data.dados);
      setTotalEncontrado(data.total_encontrado);
    }
  } catch (error) {
    console.error('Erro na busca:', error);
  } finally {
    setBuscando(false);
  }
};
```

### **Depois (com métricas):**

```typescript
// pages/busca-avancada.jsx
import { recordSearch, recordDBQuery, recordError } from '../lib/metrics';

const handleBuscar = async () => {
  setBuscando(true);
  setDados([]);

  const startTime = Date.now();

  try {
    const response = await fetch(`${API_URL}/query/filtrado`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uf: ufSelecionada || null,
        municipio: municipioSelecionado || null,
        situacao: situacaoSelecionada || null,
        limit: limiteSelecionado
      })
    });

    const data = await response.json();
    
    if (data.dados) {
      setDados(data.dados);
      setTotalEncontrado(data.total_encontrado);
      
      // 📊 Registrar métricas de sucesso
      const duration = (Date.now() - startTime) / 1000;
      recordSearch('filtros', 'success');
      recordDBQuery('filtrado', 'success', duration);
    }
  } catch (error) {
    console.error('Erro na busca:', error);
    
    // 📊 Registrar erro
    recordSearch('filtros', 'error');
    recordError('busca_filtrada', '/busca-avancada');
  } finally {
    setBuscando(false);
  }
};
```

---

## 🤖 Caso de Uso: Chat LLM

```typescript
// pages/chat-llm.jsx
import { recordLLMQuery, recordError } from '../lib/metrics';

const handleSendMessage = async () => {
  const startTime = Date.now();
  
  try {
    const response = await fetch(`${LLM_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: userMessage })
    });

    const data = await response.json();
    
    // 📊 Registrar tempo de resposta do LLM
    const duration = (Date.now() - startTime) / 1000;
    recordLLMQuery('gemma', 'success', duration);
    
    setMessages([...messages, data.response]);
  } catch (error) {
    // 📊 Registrar erro
    recordError('llm_query', '/chat-llm');
    recordLLMQuery('gemma', 'error', 0);
  }
};
```

---

## 📝 Caso de Uso: API Route

```typescript
// pages/api/empresas/[cnpj].ts
import { NextApiRequest, NextApiResponse } from 'next';
import { recordDBQuery, recordHTTPRequest, recordError } from '../../../lib/metrics';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const startTime = Date.now();
  const { cnpj } = req.query;

  try {
    // Simula consulta ao banco
    const dbStartTime = Date.now();
    const empresa = await buscarEmpresaPorCNPJ(cnpj);
    const dbDuration = (Date.now() - dbStartTime) / 1000;

    // 📊 Registrar consulta ao banco
    recordDBQuery('select_by_cnpj', 'success', dbDuration);

    // 📊 Registrar requisição HTTP
    const httpDuration = (Date.now() - startTime) / 1000;
    recordHTTPRequest('GET', `/api/empresas/${cnpj}`, 200, httpDuration);

    res.status(200).json({ empresa });
  } catch (error) {
    // 📊 Registrar erro
    recordError('database_query', `/api/empresas/${cnpj}`);
    recordHTTPRequest('GET', `/api/empresas/${cnpj}`, 500, (Date.now() - startTime) / 1000);

    res.status(500).json({ error: 'Erro ao buscar empresa' });
  }
}
```

---

## 👥 Caso de Uso: Rastreamento de Usuários Ativos

### **Middleware ou _app.jsx:**

```typescript
// pages/_app.jsx
import { useEffect } from 'react';
import { activeUsersGauge } from '../lib/metrics';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    // Incrementa ao montar
    fetch('/api/user-enter', { method: 'POST' });

    // Decrementa ao desmontar
    return () => {
      fetch('/api/user-leave', { method: 'POST' });
    };
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
```

### **API Routes:**

```typescript
// pages/api/user-enter.ts
import { activeUsersGauge } from '../../lib/metrics';

export default async function handler(req, res) {
  activeUsersGauge.inc(); // Incrementa usuários ativos
  res.status(200).json({ ok: true });
}

// pages/api/user-leave.ts
import { activeUsersGauge } from '../../lib/metrics';

export default async function handler(req, res) {
  activeUsersGauge.dec(); // Decrementa usuários ativos
  res.status(200).json({ ok: true });
}
```

---

## 📊 Caso de Uso: Geração de Relatórios

```typescript
// lib/relatorios.ts
import { recordReport } from './metrics';

export async function gerarRelatorioPDF(dados) {
  try {
    const pdf = await criarPDF(dados);
    
    // 📊 Registrar sucesso
    recordReport('pdf', 'success');
    
    return pdf;
  } catch (error) {
    // 📊 Registrar erro
    recordReport('pdf', 'error');
    throw error;
  }
}

export async function gerarRelatorioExcel(dados) {
  try {
    const excel = await criarExcel(dados);
    
    // 📊 Registrar sucesso
    recordReport('excel', 'success');
    
    return excel;
  } catch (error) {
    // 📊 Registrar erro
    recordReport('excel', 'error');
    throw error;
  }
}
```

---

## 🗄️ Caso de Uso: Cache

```typescript
// lib/cache.ts
import { cacheSizeGauge } from './metrics';

class QueryCache {
  private cache = new Map();

  set(key: string, value: any) {
    this.cache.set(key, value);
    
    // 📊 Atualizar tamanho do cache
    cacheSizeGauge.set({ cache_type: 'query' }, this.cache.size);
  }

  get(key: string) {
    return this.cache.get(key);
  }

  delete(key: string) {
    this.cache.delete(key);
    
    // 📊 Atualizar tamanho do cache
    cacheSizeGauge.set({ cache_type: 'query' }, this.cache.size);
  }

  clear() {
    this.cache.clear();
    
    // 📊 Resetar tamanho do cache
    cacheSizeGauge.set({ cache_type: 'query' }, 0);
  }
}
```

---

## 📈 Visualizando no Grafana

Após instrumentar suas páginas, crie painéis no Grafana:

### **Painel: Buscas por Tipo**
```promql
sum by (search_type) (rate(crm_searches_total[5m]))
```

### **Painel: Tempo Médio de Consulta ao Banco**
```promql
rate(crm_db_query_duration_seconds_sum[5m]) / 
rate(crm_db_query_duration_seconds_count[5m])
```

### **Painel: Taxa de Erros por Página**
```promql
sum by (page) (rate(crm_errors_total[5m]))
```

### **Painel: Distribuição de Tempo de Resposta LLM**
```promql
histogram_quantile(0.95, 
  sum(rate(crm_llm_query_duration_seconds_bucket[5m])) by (le)
)
```

### **Painel: Relatórios Gerados (últimas 24h)**
```promql
increase(crm_reports_generated_total[24h])
```

---

## 🎯 Boas Práticas

### ✅ DO:
- ✅ Registre métricas em operações críticas (buscas, consultas, erros)
- ✅ Use labels para categorizar (tipo de busca, tipo de erro)
- ✅ Meça tempo de operações assíncronas
- ✅ Registre tanto sucessos quanto falhas

### ❌ DON'T:
- ❌ Não registre métricas em loops (use agregação)
- ❌ Não use muitos labels diferentes (cardinalidade alta)
- ❌ Não registre dados sensíveis (senhas, tokens)
- ❌ Não esqueça de registrar erros

---

## 🔍 Testando Métricas

### Via Browser Console:
```javascript
// Testar se métricas estão sendo expostas
fetch('/api/metrics')
  .then(r => r.text())
  .then(console.log)
```

### Via Prometheus:
1. Acesse http://localhost:9090
2. Query: `crm_searches_total`
3. Execute e veja os dados

### Via Grafana:
1. Acesse http://localhost:3002
2. Explore → Prometheus
3. Query: `rate(crm_searches_total[5m])`
4. Run Query

---

## 📚 Métricas Disponíveis

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `crm_searches_total` | Counter | Total de buscas |
| `crm_llm_query_duration_seconds` | Histogram | Duração de consultas LLM |
| `crm_db_query_duration_seconds` | Histogram | Duração de consultas ao BD |
| `crm_errors_total` | Counter | Total de erros |
| `crm_active_users` | Gauge | Usuários ativos |
| `crm_http_requests_total` | Counter | Requisições HTTP |
| `crm_http_request_duration_seconds` | Histogram | Duração de requisições |
| `crm_reports_generated_total` | Counter | Relatórios gerados |
| `crm_cache_size_items` | Gauge | Tamanho do cache |

---

**🎉 Pronto! Agora você sabe como instrumentar sua aplicação!**

