# 🔐 Configuração do Login com Google (OAuth)

Este guia explica como configurar a autenticação com Google no Supabase.

## 📋 Pré-requisitos

- Conta no Supabase (https://app.supabase.com)
- Conta no Google Cloud Console (https://console.cloud.google.com)

---

## 🚀 Passo a Passo

### 1. Configurar no Google Cloud Console

#### 1.1 Criar um Projeto

1. Acesse: https://console.cloud.google.com
2. Clique em **"Select a project"** → **"New Project"**
3. Nome do projeto: `CRM Auth` (ou outro nome)
4. Clique em **"Create"**

#### 1.2 Configurar OAuth Consent Screen

1. No menu lateral, vá em: **APIs & Services** → **OAuth consent screen**
2. Escolha **"External"** e clique em **"Create"**
3. Preencha as informações:
   - **App name:** CRM Application
   - **User support email:** seu-email@gmail.com
   - **Developer contact:** seu-email@gmail.com
4. Clique em **"Save and Continue"** (pode pular as telas de Scopes e Test users)
5. Clique em **"Back to Dashboard"**

#### 1.3 Criar Credenciais OAuth

1. No menu lateral, vá em: **APIs & Services** → **Credentials**
2. Clique em **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Escolha:
   - **Application type:** Web application
   - **Name:** CRM Web Client
4. Em **"Authorized JavaScript origins"**, adicione:
   ```
   http://localhost:3000
   ```
5. Em **"Authorized redirect URIs"**, adicione a URL do Supabase:
   ```
   https://SEU-PROJETO.supabase.co/auth/v1/callback
   ```
   ⚠️ **IMPORTANTE:** Substitua `SEU-PROJETO` pelo ID real do seu projeto Supabase
   
   Para encontrar essa URL:
   - Vá no Supabase → Settings → API
   - Copie a **Project URL** e adicione `/auth/v1/callback` no final

6. Clique em **"Create"**

7. **Guarde as credenciais:**
   - **Client ID:** `123456789-abcdefg.apps.googleusercontent.com`
   - **Client Secret:** `GOCSPX-xxxxxxxxxxxxx`

---

### 2. Configurar no Supabase

#### 2.1 Ativar Google Provider

1. Acesse seu projeto no Supabase: https://app.supabase.com
2. Vá em: **Authentication** → **Providers**
3. Encontre **Google** na lista e clique para expandir
4. **Ative** o toggle "Enable Sign in with Google"
5. Cole as credenciais do Google:
   - **Client ID:** (cole o Client ID do Google Cloud Console)
   - **Client Secret:** (cole o Client Secret)
6. Clique em **"Save"**

#### 2.2 Desabilitar Confirmação de Email (Opcional)

Para facilitar o desenvolvimento, você pode desabilitar a confirmação de email:

1. No Supabase, vá em: **Authentication** → **Providers** → **Email**
2. Desabilite: **"Confirm email"**
3. Clique em **"Save"**

---

### 3. Adicionar URL de Produção (Quando Deploy)

Quando você fizer deploy da aplicação:

#### No Google Cloud Console:

1. Vá em **Credentials** → Edite seu OAuth client
2. Adicione em **"Authorized JavaScript origins"**:
   ```
   https://seu-dominio.com
   ```
3. Adicione em **"Authorized redirect URIs"**:
   ```
   https://SEU-PROJETO.supabase.co/auth/v1/callback
   ```

#### No Supabase:

1. Vá em **Authentication** → **URL Configuration**
2. Adicione sua URL de produção em **"Site URL"**

---

## ✅ Testar a Autenticação

### Teste com Email/Senha:

1. Acesse: http://localhost:3000
2. Clique em **"Não tem conta? Cadastre-se"**
3. Preencha email e senha (mínimo 6 caracteres)
4. Clique em **"Criar Conta"**
5. Verifique seu email (se confirmação estiver ativa) ou faça login diretamente

### Teste com Google:

1. Acesse: http://localhost:3000
2. Clique no botão **"Google"**
3. Escolha sua conta Google
4. Autorize o acesso
5. Você será redirecionado para `/dashboard`

---

## 🔧 Troubleshooting

### Erro: "redirect_uri_mismatch"

**Solução:** A URI de redirecionamento não está configurada corretamente.

1. Verifique se a URI no Google Cloud Console está exatamente assim:
   ```
   https://SEU-PROJETO.supabase.co/auth/v1/callback
   ```
2. Substitua `SEU-PROJETO` pelo ID real do seu projeto Supabase
3. Certifique-se de usar `https://` (não `http://`)

### Erro: "Invalid client"

**Solução:** Client ID ou Secret incorretos.

1. Copie novamente as credenciais do Google Cloud Console
2. Cole no Supabase e clique em **"Save"**
3. Aguarde alguns segundos para propagar

### Login com Google não funciona em localhost

**Solução:** Certifique-se de que `http://localhost:3000` está nas **"Authorized JavaScript origins"**

### Cadastro com email não funciona

**Solução:** Verifique se:
1. O Supabase está configurado com SMTP válido (ou use o serviço padrão)
2. Verifique a caixa de spam do seu email
3. Ou desabilite a confirmação de email (apenas para desenvolvimento)

---

## 📚 Recursos Adicionais

- [Documentação Supabase - Google OAuth](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Google Cloud Console](https://console.cloud.google.com)
- [Supabase Auth](https://supabase.com/docs/guides/auth)

---

## 🔒 Segurança

⚠️ **NUNCA** commite suas credenciais no Git!

- As credenciais devem estar apenas no `.env.local` (que está no `.gitignore`)
- Client ID e Client Secret do Google devem ficar apenas no Supabase Dashboard
- Use variáveis de ambiente em produção


