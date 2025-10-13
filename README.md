# CRM - Sistema de Consulta com IA

Sistema de gerenciamento de dados CNPJ com interface Next.js e backend Supabase.

## 🚀 Início Rápido

### Pré-requisitos
- Docker e Docker Compose instalados
- Node.js 18+ (para desenvolvimento local)

### Executar com Docker

1. **Iniciar todo o stack (recomendado):**
```bash
docker compose up --build
```

2. **Ou iniciar apenas o frontend:**
```bash
docker compose up --build next-app
```

### Acessar a Aplicação

- **Frontend:** http://localhost:3000
- **Supabase Studio:** http://localhost:54323
- **API Backend:** http://localhost:5000

## 📁 Estrutura do Projeto

```
CRM/
├── app/                    # Aplicação Next.js (App Router)
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página inicial
│   └── globals.css        # Estilos globais
├── public/                # Assets estáticos
├── Dockerfile             # Configuração Docker do frontend
├── docker-compose.yml     # Orquestração dos containers
├── package.json           # Dependências do projeto
├── next.config.js         # Configuração do Next.js
└── tailwind.config.js     # Configuração do Tailwind CSS
```

## 🛠️ Desenvolvimento Local (sem Docker)

1. Instalar dependências:
```bash
npm install
```

2. Executar em modo de desenvolvimento:
```bash
npm run dev
```

3. Abrir http://localhost:3000

## 🐳 Comandos Docker Úteis

```bash
# Parar todos os containers
docker compose down

# Ver logs
docker compose logs -f next-app

# Reconstruir após mudanças
docker compose up --build next-app

# Limpar volumes (cuidado!)
docker compose down -v
```

## 📦 Tecnologias

- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend:** Supabase (PostgreSQL, Auth, API)
- **Containerização:** Docker, Docker Compose
- **Bibliotecas:** jsPDF, jspdf-autotable

## 🎯 Funcionalidades

- ✅ Consulta ao banco de dados com linguagem natural
- ✅ Visualização de resultados em tabela
- ✅ Exportação para CSV e PDF
- ✅ Interface moderna e responsiva
- ✅ Comunicação com API Flask de IA

## 📝 Notas

- O backend Flask deve estar rodando na porta 5000
- O Supabase deve estar inicializado (`npx supabase start`)
- Certifique-se de que todas as portas necessárias estão disponíveis


