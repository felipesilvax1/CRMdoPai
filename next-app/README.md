# CRM - Frontend Next.js com Autenticação Supabase

Este é o frontend da aplicação CRM desenvolvido com Next.js e Supabase para autenticação e banco de dados.

## 🚀 Características

- ✅ Autenticação completa com Supabase (Login/Logout)
- ✅ **Cadastro de novos usuários (Sign Up)**
- ✅ **Login com Google (OAuth/SSO)**
- ✅ Proteção de rotas (Middleware de autenticação)
- ✅ Dashboard protegido para usuários autenticados
- ✅ Interface moderna com Tailwind CSS
- ✅ Gerenciamento de sessão automático
- ✅ Exibição de dados em tabela responsiva

## 📦 Instalação

### 1. Instalar dependências

```bash
npm install
```

### 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e configure suas credenciais do Supabase:

```bash
cp .env.local.example .env.local
```

Edite o arquivo `.env.local` e adicione suas credenciais:

```env
NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua-chave-anon-key-aqui
```

### 3. Iniciar o servidor de desenvolvimento

```bash
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000) no seu navegador.

## 📁 Estrutura do Projeto

```
next-app/
├── components/
│   ├── AuthForm.jsx       # Formulário de login
│   └── DataTable.jsx      # Componente de tabela de dados
├── lib/
│   └── supabaseClient.js  # Cliente do Supabase
├── pages/
│   ├── _app.jsx           # Configuração global do App
│   ├── index.jsx          # Página de login
│   └── dashboard.jsx      # Dashboard protegido
├── styles/
│   └── globals.css        # Estilos globais (Tailwind)
└── .env.local.example     # Exemplo de variáveis de ambiente
```

## 🔐 Fluxo de Autenticação

### Opção 1: Email e Senha

1. **Cadastro**: Usuário acessa `/` → clica em "Não tem conta? Cadastre-se"
2. **Criar Conta**: Preenche email e senha (mínimo 6 caracteres) → clica em "Criar Conta"
3. **Confirmação**: Verifica email (se confirmação estiver ativa) ou é redirecionado automaticamente
4. **Login**: Faz login com as credenciais criadas
5. **Dashboard**: É redirecionado para `/dashboard`

### Opção 2: Login com Google (SSO)

1. **Google OAuth**: Usuário acessa `/` → clica no botão "Google"
2. **Autorização**: É redirecionado para o Google → autoriza o acesso
3. **Dashboard**: É redirecionado automaticamente para `/dashboard`

### Proteção e Logout

- **Proteção**: Se tentar acessar `/dashboard` sem estar autenticado, é redirecionado para `/`
- **Logout**: Botão "Sair" no dashboard encerra a sessão e redireciona para login
- **Sessão Persistente**: Se já estiver logado, ao acessar `/` é redirecionado direto para `/dashboard`

## ⚙️ Configuração do Supabase

### 1. Configurar Autenticação com Email

1. No Supabase, vá em: **Authentication** → **Providers** → **Email**
2. Certifique-se de que está **ativado**
3. Para desenvolvimento, você pode desabilitar **"Confirm email"**
4. Clique em **"Save"**

### 2. Configurar Login com Google (Opcional mas Recomendado)

Para ativar o login com Google, siga o guia completo:

📖 **[SETUP_GOOGLE_AUTH.md](./SETUP_GOOGLE_AUTH.md)**

Resumo rápido:
1. Criar projeto no Google Cloud Console
2. Configurar OAuth Consent Screen
3. Criar credenciais OAuth 2.0
4. Ativar Google Provider no Supabase
5. Adicionar Client ID e Secret

### 3. Criar uma tabela protegida

No seu projeto Supabase, crie uma tabela de exemplo:

```sql
CREATE TABLE sua_tabela_protegida (
  id SERIAL PRIMARY KEY,
  nome TEXT,
  email TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Configurar políticas RLS (Row Level Security)

```sql
-- Habilitar RLS
ALTER TABLE sua_tabela_protegida ENABLE ROW LEVEL SECURITY;

-- Permitir leitura apenas para usuários autenticados
CREATE POLICY "Usuários autenticados podem ler"
ON sua_tabela_protegida FOR SELECT
TO authenticated
USING (true);
```

### 5. Atualizar o código do Dashboard

No arquivo `pages/dashboard.jsx`, altere a linha 21:

```javascript
// De:
.from('sua_tabela_protegida')

// Para:
.from('nome_da_sua_tabela')
```

## 🎨 Personalização

### Alterar cores do tema

Edite o arquivo `components/AuthForm.jsx` e `pages/dashboard.jsx` para modificar as classes do Tailwind CSS.

### Adicionar novos campos ao formulário

Modifique o componente `AuthForm.jsx` para incluir novos campos como nome, telefone, etc.

## 📝 Scripts Disponíveis

- `npm run dev` - Inicia o servidor de desenvolvimento
- `npm run build` - Cria a build de produção
- `npm start` - Inicia o servidor de produção
- `npm run lint` - Executa o linter

## 🔧 Troubleshooting

### Erro: "Invalid API key"
- Verifique se as variáveis de ambiente estão corretas no `.env.local`
- Certifique-se de que o arquivo `.env.local` está na raiz do projeto

### Erro: "Permission denied"
- Verifique se as políticas RLS estão configuradas corretamente no Supabase
- Certifique-se de que o usuário está autenticado

### Página em branco após login
- Abra o console do navegador (F12) para ver erros
- Verifique se o nome da tabela no dashboard está correto

## 📚 Recursos Adicionais

- [Documentação do Next.js](https://nextjs.org/docs)
- [Documentação do Supabase](https://supabase.com/docs)
- [Documentação do Tailwind CSS](https://tailwindcss.com/docs)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é privado e de uso interno.

