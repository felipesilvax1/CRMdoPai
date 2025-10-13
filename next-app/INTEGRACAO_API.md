# 🔌 Integração com API Local (PostgreSQL)

Este documento explica como a aplicação Next.js se integra com a API local Python/Flask que conecta ao PostgreSQL.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      USUÁRIO                                │
│                    (Navegador)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Next.js Frontend                               │
│            http://localhost:3000                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Autenticação: Supabase Auth                         │  │
│  │  Dados: API Local (PostgreSQL)                       │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────┬───────────────────────┘
                    │                 │
         ┌──────────┘                 └──────────┐
         ▼                                       ▼
┌─────────────────────┐              ┌──────────────────────┐
│   Supabase Auth     │              │   API Local Flask    │
│   (Autenticação)    │              │  localhost:5000      │
│                     │              │  (Container Docker)  │
└─────────────────────┘              └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │   PostgreSQL         │
                                     │   (cnpj_processed)   │
                                     │   192.168.15.24      │
                                     └──────────────────────┘
```

## 🚀 Como Funciona

### 1. **Autenticação (Supabase)**
- Usuário faz login/cadastro via Supabase Auth
- JWT token é gerenciado automaticamente pelo Supabase SDK
- Sessão é verificada em todas as páginas protegidas

### 2. **Dados (API Local PostgreSQL)**
- Após autenticação, o Dashboard busca dados da API local
- A API está em Python/Flask rodando em container Docker
- Conecta diretamente ao PostgreSQL do projeto CRM

## 📁 Arquivos Principais

### Frontend (Next.js)

#### `lib/apiClient.js`
Cliente JavaScript para comunicar com a API local:

```javascript
import { getEmpresas, checkApiHealth } from '../lib/apiClient';

// Verificar saúde da API
const health = await checkApiHealth();

// Buscar empresas
const result = await getEmpresas(50);
```

**Funções disponíveis:**
- `checkApiHealth()` - Verifica status da API
- `queryDatabase(question)` - Consulta genérica
- `getStatistics()` - Estatísticas gerais
- `getEmpresas(limit)` - Lista de empresas
- `executeCustomSQL(sql)` - SQL customizado

#### `pages/dashboard.jsx`
Página principal que:
1. Verifica autenticação (Supabase)
2. Conecta na API local
3. Exibe dados em tabela

### Backend (API Python)

#### `api/app.py`
API Flask com dois endpoints:

**GET** `/health` - Status da API
```json
{
  "status": "ok",
  "database": "PostgreSQL",
  "host": "cnpj_postgres_final",
  "message": "API funcionando!"
}
```

**POST** `/query` - Executar consultas
```json
// Request
{
  "question": "empresas"
}

// Response
{
  "resposta_texto": "Encontrei 20 resultados.",
  "sql_gerado": "SELECT ...",
  "total_resultados": 20,
  "dados_completos": [...]
}
```

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Arquivo: `next-app/.env.local`

```env
# Supabase (Autenticação)
NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua-chave-anon-key

# API Local (Dados PostgreSQL)
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 2. Iniciar a API

#### Opção 1: Docker Compose (Recomendado)

```bash
# Inicia apenas a API
docker-compose up -d api

# Verificar logs
docker logs crm-api

# Testar endpoint
curl http://localhost:5000/health
```

#### Opção 2: Python Direto

```bash
cd api
pip install -r requirements.txt

# Configurar variáveis
export USE_POSTGRES=true
export DB_HOST=192.168.15.24
export DB_PORT=5432
export DB_NAME=cnpj_processed
export DB_USER=postgres
export DB_PASSWORD=password

# Iniciar
python app.py
```

### 3. Iniciar o Frontend

```bash
cd next-app
npm run dev
```

Acesse: http://localhost:3000

## 🔍 Testando a Integração

### 1. Verificar API

```bash
# Windows PowerShell
curl.exe http://localhost:5000/health

# Linux/Mac
curl http://localhost:5000/health
```

**Resposta esperada:**
```json
{"status":"ok","database":"PostgreSQL","host":"cnpj_postgres_final"}
```

### 2. Testar Consulta

```bash
# Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:5000/query" -Method POST -Body '{"question":"empresas"}' -ContentType "application/json"
```

### 3. No Frontend

1. Acesse http://localhost:3000
2. Faça login (ou cadastre-se)
3. Você será redirecionado para `/dashboard`
4. Verifique:
   - **Indicador verde** = API conectada ✅
   - **Indicador vermelho** = API desconectada ❌
   - **Tabela** = Dados do PostgreSQL

## 🐛 Troubleshooting

### API não responde

**Problema:** `ERR_CONNECTION_REFUSED` ao acessar localhost:5000

**Solução:**
```bash
# Verificar se container está rodando
docker ps | grep crm-api

# Se não estiver, iniciar
docker-compose up -d api

# Ver logs de erro
docker logs crm-api
```

### Erro de conexão com PostgreSQL

**Problema:** API retorna erro 500 no `/health`

**Verificar:**
1. PostgreSQL está acessível?
```bash
docker ps | grep postgres
```

2. Configuração correta no `docker-compose.yml`:
```yaml
environment:
  - DB_HOST=cnpj_postgres_final  # Nome do container
  - DB_NAME=cnpj_processed       # Nome do banco
  - DB_USER=postgres
  - DB_PASSWORD=password
```

3. Containers na mesma rede?
```bash
docker network ls
docker network inspect bridge
```

### Frontend não busca dados

**Problema:** Dashboard carrega mas não mostra dados

**Verificar:**
1. Arquivo `.env.local` tem `NEXT_PUBLIC_API_URL`?
2. Servidor Next.js foi **reiniciado** após adicionar variável?
   ```bash
   # Pare o servidor (Ctrl+C)
   cd next-app
   npm run dev
   ```
3. Console do navegador (F12) mostra erros?

### CORS Error

**Problema:** "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solução:** A API já tem CORS habilitado:
```python
from flask_cors import CORS
CORS(app)
```

Se ainda der erro, adicione configuração específica:
```python
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
```

## 📊 Exemplos de Uso

### Buscar Estatísticas

```javascript
import { getStatistics } from '../lib/apiClient';

const stats = await getStatistics();
console.log(stats.data.dados_completos);
// [{total_empresas: 1000000, total_estabelecimentos: 1500000, ...}]
```

### Buscar Empresas

```javascript
import { getEmpresas } from '../lib/apiClient';

const result = await getEmpresas(100);
if (result.success) {
  const empresas = result.data.dados_completos;
  // [{ "cnpj basico": "12345678", "razao social": "...", ... }]
}
```

### Consulta Customizada

```javascript
import { queryDatabase } from '../lib/apiClient';

const result = await queryDatabase('total de empresas');
console.log(result.data.resposta_texto);
// "Base de dados: 1.000.000 empresas, 1.500.000 estabelecimentos."
```

## 🔐 Segurança

### Separação de Responsabilidades

- ✅ **Autenticação:** Gerenciada pelo Supabase (seguro, escalável)
- ✅ **Autorização:** JWT tokens automáticos
- ✅ **Dados:** API local com acesso direto ao PostgreSQL

### Boas Práticas

1. **Nunca** exponha a API diretamente na internet sem autenticação
2. **Use** a API apenas em rede local/confiável
3. **Valide** credenciais do Supabase antes de permitir acesso à API
4. **Considere** adicionar autenticação JWT na API para produção

### Para Produção

Se for expor a API publicamente:

```python
# api/app.py - Adicionar verificação de token

from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"erro": "Token não fornecido"}), 401
        
        try:
            # Verificar token do Supabase
            jwt.decode(token, SUPABASE_SECRET, algorithms=['HS256'])
        except:
            return jsonify({"erro": "Token inválido"}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/query', methods=['POST'])
@require_auth
def handle_query():
    # ...
```

## 📚 Próximos Passos

1. **Expandir API:** Adicionar mais endpoints específicos
2. **Cache:** Implementar cache Redis para consultas frequentes
3. **WebSocket:** Real-time updates usando Socket.IO
4. **Gráficos:** Integrar Chart.js/Recharts no Dashboard
5. **Filtros:** Adicionar filtros avançados na interface

## 🤝 Contribuindo

Ao adicionar novos recursos:

1. **Backend:** Adicione novos endpoints em `api/app.py`
2. **Frontend:** Adicione novas funções em `lib/apiClient.js`
3. **UI:** Atualize componentes em `pages/` e `components/`
4. **Docs:** Atualize esta documentação

---

**Desenvolvido para:** CRM Project
**Stack:** Next.js 14 + Python Flask + PostgreSQL + Supabase Auth


