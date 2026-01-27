# 🔒 Guia de Segurança - Remover Senha do Repositório

## ⚠️ PROBLEMA IDENTIFICADO

O arquivo `.streamlit/secrets.toml` com sua senha está sendo rastreado pelo Git e pode estar no repositório público!

## ✅ SOLUÇÃO

Execute os seguintes comandos para remover o arquivo do Git (mas mantê-lo localmente):

```bash
# 1. Remover o arquivo do índice do Git (mas manter localmente)
git rm --cached .streamlit/secrets.toml

# 2. Adicionar o .gitignore (se ainda não foi commitado)
git add .gitignore

# 3. Fazer commit das mudanças
git commit -m "🔒 Adicionar .gitignore e remover secrets.toml do repositório"

# 4. Fazer push
git push origin main
```

## 📝 IMPORTANTE

1. **O arquivo `.streamlit/secrets.toml` continuará existindo localmente** - você ainda poderá usar o app localmente
2. **O arquivo NÃO será mais commitado** - graças ao `.gitignore`
3. **No Streamlit Cloud**, configure a senha através da interface web (Settings → Secrets)
4. **Se a senha já foi exposta no GitHub**, considere trocá-la por uma nova senha

## 🔐 Configuração no Streamlit Cloud

1. Acesse seu app no Streamlit Cloud
2. Vá em **Settings** (⚙️) → **Secrets**
3. Adicione:
   ```toml
   SENHA_ADMIN = "sua_nova_senha_segura"
   ```
4. Salve e aguarde o app reiniciar

## ✅ Verificação

Após executar os comandos, verifique que o arquivo não está mais sendo rastreado:

```bash
git ls-files .streamlit/secrets.toml
```

Se não retornar nada, está correto! ✅
