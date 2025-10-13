# 🚀 Modo de Desenvolvimento - Bypass de Autenticação

## ✅ O QUE FOI FEITO

Criei um **modo de desenvolvimento** que permite testar o sistema **SEM precisar configurar o Supabase**!

### Como funciona:

- ✅ Autenticação do Supabase **desabilitada**
- ✅ Acesso direto ao Dashboard **sem login**
- ✅ Dados do PostgreSQL **funcionando normalmente**
- ✅ Você pode testar tudo **sem criar conta**

---

## 🎯 COMO USAR AGORA

### 1. O servidor vai reiniciar automaticamente

Aguarde alguns segundos...

### 2. Acesse a aplicação

```
http://localhost:3000
```

### 3. Você verá esta tela:

```
┌─────────────────────────────────────────┐
│     🚀 Modo Desenvolvimento             │
│   Autenticação desabilitada para testes │
│                                         │
│  ℹ️ Você está no modo de desenvolvimento│
│     A autenticação do Supabase está     │
│     desabilitada.                       │
│                                         │
│  [  Entrar no Dashboard (Sem Login)  ] │
│                                         │
│  Para habilitar autenticação real,      │
│  configure o Supabase e altere          │
│  NEXT_PUBLIC_DEV_MODE=false             │
└─────────────────────────────────────────┘
```

### 4. Clique no botão

**"Entrar no Dashboard (Sem Login)"**

### 5. Pronto! 🎉

Você será redirecionado para o Dashboard e verá:
- ✅ Dados reais do seu PostgreSQL
- ✅ Tabela de empresas
- ✅ Indicador de status da API
- ✅ Tudo funcionando sem autenticação!

---

## 🔧 CONFIGURAÇÃO

O modo dev está **ATIVADO** através do arquivo `.env.local`:

```env
# Modo de Desenvolvimento (bypass autenticação para testes)
NEXT_PUBLIC_DEV_MODE=true
```

### Para DESABILITAR o modo dev (quando quiser usar autenticação real):

Edite: `C:\Users\PwC\Documents\CRM\next-app\.env.local`

```env
# Mudar de true para false
NEXT_PUBLIC_DEV_MODE=false
```

E reinicie o servidor:
```bash
# Ctrl+C para parar
cd next-app
npm run dev
```

---

## 🎨 DIFERENÇAS ENTRE MODOS

### Modo Desenvolvimento (NEXT_PUBLIC_DEV_MODE=true)

| Feature | Status |
|---------|--------|
| Login com Supabase | ❌ Desabilitado |
| Cadastro | ❌ Desabilitado |
| Login com Google | ❌ Desabilitado |
| Acesso ao Dashboard | ✅ Direto, sem login |
| Dados da API | ✅ Funcionando |
| Logout | ✅ Limpa sessão local |
| Indicador no Dashboard | 🟡 "(Modo Dev)" |

### Modo Produção (NEXT_PUBLIC_DEV_MODE=false)

| Feature | Status |
|---------|--------|
| Login com Supabase | ✅ Ativo |
| Cadastro | ✅ Ativo |
| Login com Google | ✅ Ativo (se configurado) |
| Acesso ao Dashboard | 🔒 Requer autenticação |
| Dados da API | ✅ Funcionando |
| Logout | ✅ Encerra sessão Supabase |
| Indicador no Dashboard | ➖ Normal |

---

## 🔍 O QUE TESTAR AGORA

Com o modo dev ativo, você pode testar:

### 1. Dashboard
- ✅ Visualizar dados do PostgreSQL
- ✅ Ver tabela de empresas
- ✅ Verificar conexão com API
- ✅ Testar funcionalidade de Logout

### 2. API Local
- ✅ Confirmar que dados estão sendo carregados
- ✅ Verificar indicador de status (verde/vermelho)
- ✅ Ver quantos registros são retornados

### 3. Performance
- ✅ Tempo de carregamento da página
- ✅ Tempo de resposta da API
- ✅ Responsividade da interface

---

## 🐛 TROUBLESHOOTING

### Erro: Ainda aparece o formulário de login/cadastro

**Causa:** Servidor não reiniciou com a nova variável

**Solução:**
1. Pare o servidor (Ctrl+C)
2. Reinicie: `npm run dev`
3. Aguarde aparecer: `✓ Ready in X.Xs`
4. Recarregue a página (F5)

### Dashboard não carrega dados

**Causa:** API não está rodando

**Solução:**
```bash
# Verificar se API está rodando
docker ps | grep crm-api

# Se não estiver, iniciar
docker-compose up -d api

# Verificar logs
docker logs crm-api
```

### Erro: "dev_user" not found

**Causa:** LocalStorage foi limpo

**Solução:**
1. Volte para http://localhost:3000
2. Clique novamente em "Entrar no Dashboard (Sem Login)"

---

## 📊 EXEMPLO DE FLUXO

```
1. Acessar http://localhost:3000
   ↓
2. Ver tela "🚀 Modo Desenvolvimento"
   ↓
3. Clicar em "Entrar no Dashboard (Sem Login)"
   ↓
4. Redirecionado para /dashboard
   ↓
5. Ver dados do PostgreSQL:
   - Dashboard CRM (Modo Dev)
   - Logado como: dev@teste.com
   - 🟢 API: PostgreSQL (cnpj_postgres_final)
   - Tabela com empresas
   ↓
6. Testar sistema normalmente!
```

---

## 🔒 SEGURANÇA

⚠️ **IMPORTANTE:**

- Este modo é **APENAS PARA DESENVOLVIMENTO LOCAL**
- **NUNCA** use em produção
- **SEMPRE** mude para `NEXT_PUBLIC_DEV_MODE=false` antes de fazer deploy
- A autenticação real (Supabase) deve ser configurada para produção

### Checklist antes do Deploy:

- [ ] `NEXT_PUBLIC_DEV_MODE=false` no `.env.local`
- [ ] Supabase configurado com credenciais reais
- [ ] Testar autenticação em ambiente de staging
- [ ] Remover usuários de desenvolvimento
- [ ] Habilitar confirmação de email

---

## 🎯 PRÓXIMOS PASSOS

### Enquanto testa o sistema:

Você pode:
1. ✅ Explorar o Dashboard
2. ✅ Verificar integração com PostgreSQL
3. ✅ Testar performance
4. ✅ Identificar melhorias na UI/UX

### Quando estiver pronto:

Para habilitar autenticação real:
1. Configure o Supabase (guia: `SETUP_GOOGLE_AUTH.md`)
2. Atualize `.env.local` com credenciais
3. Mude `NEXT_PUBLIC_DEV_MODE=false`
4. Reinicie o servidor
5. Teste login/cadastro real

---

## 📝 LOGS E DEBUG

### Ver logs da API:
```bash
docker logs crm-api --tail 50 -f
```

### Ver logs do Next.js:
```bash
# No terminal onde rodou npm run dev
# Ou console do navegador (F12 > Console)
```

### Testar API manualmente:
```bash
# Health check
curl.exe http://localhost:5000/health

# Query de empresas
Invoke-RestMethod -Uri "http://localhost:5000/query" -Method POST -Body '{"question":"empresas"}' -ContentType "application/json"
```

---

## 🤝 FEEDBACK

Este modo foi criado especificamente para permitir testes rápidos sem depender do Supabase.

Se encontrar problemas ou tiver sugestões, me avise!

---

**Status:** ✅ **ATIVO**  
**Data:** 13/10/2025  
**Variável:** `NEXT_PUBLIC_DEV_MODE=true`


