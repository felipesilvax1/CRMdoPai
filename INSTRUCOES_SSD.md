# 💾 Migração via SSD Externo - MÉTODO MAIS RÁPIDO

## ⏱️ Tempo Total Estimado: 45-60 minutos

---

## 📋 PASSO A PASSO:

### **PARTE 1: No T14 (15-20 min)**

1. **Conecte o SSD externo no T14**
   - Anote a letra da unidade (ex: D:, E:, F:)

2. **Abra PowerShell como Administrador no T14**

3. **Execute:**
   ```powershell
   cd \caminho\do\script
   .\1_DUMP_NO_T14.ps1
   ```

4. **Aguarde:** 15-25 minutos
   - Vai criar: `D:\dump_cnpj_processed` (15-25 GB)
   - Usando 8 threads paralelas

5. **Quando terminar:**
   - ✅ Verifique se pasta foi criada no SSD
   - ⏏️ Desconecte o SSD com segurança

---

### **PARTE 2: Transferência Física**

6. **Remova o SSD do T14**
7. **Conecte o SSD no PC principal**
8. **Anote a letra da unidade no PC** (pode ser diferente!)

---

### **PARTE 3: No PC Principal (30-40 min)**

9. **Execute:**
   ```powershell
   .\2_RESTORE_NO_PC.ps1
   ```

10. **Aguarde:** 30-40 minutos
    - Restore paralelo com 8 threads
    - Usando todos os cores do Xeon

11. **Validação automática** ao final

---

## ⚡ **Por que isso é MUITO mais rápido:**

| Método | Velocidade | Tempo |
|--------|-----------|-------|
| Via Rede (atual) | 8.5 MB/s | 2-3 horas |
| **Via SSD** | **100-150 MB/s** | **45-60 min** |

**Diferença: 10-15x mais rápido!** 🚀

---

## 🔧 **Ajustes Necessários:**

Antes de executar os scripts, **EDITE** a linha:
```powershell
$SSD_PATH = "D:"  # Mude para a letra correta!
```

**No T14:** verifique a letra no Explorador de Arquivos  
**No PC:** pode ser diferente, verifique novamente!

---

## ✅ **Checklist:**

**Antes de começar:**
- [ ] SSD com 30+ GB livres
- [ ] Scripts copiados para o T14
- [ ] PowerShell como Admin

**No T14:**
- [ ] SSD conectado e reconhecido
- [ ] Script 1 executado
- [ ] Dump criado (15-25 GB)
- [ ] SSD desconectado com segurança

**No PC:**
- [ ] SSD conectado
- [ ] Script 2 executado  
- [ ] Validação passou
- [ ] API atualizada

---

## 🎯 **Próximo Passo AGORA:**

**Copie o arquivo `1_DUMP_NO_T14.ps1` para o T14 e execute lá!**

Pode ser via:
- Pen drive
- Email para si mesmo
- OneDrive/Google Drive
- Ou simplesmente crie o arquivo lá e cole o conteúdo

**Quando terminar no T14, me avise que preparo o PC!** 📱





