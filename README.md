# 📋 Planilhado

Aplicativo web simples para controle de planilhado de hunts, desenvolvido com Streamlit.

## 🎯 Funcionalidades

- **Cadastro de Hunts**: Formulário simples para registrar hunts com respawn, horários e integrantes
- **Autocomplete de Respawns**: Sugestão automática de respawns já cadastrados
- **Validação de Overlaps**: Impede cadastros com conflito de horário no mesmo respawn
- **Visualização por Respawn**: Quadros organizados mostrando todas as hunts agrupadas por respawn
- **Controle de Acesso**: Visualização pública, mas edição protegida por senha
- **Dark Mode**: Interface com tema escuro
- **Banco de Dados SQLite**: Fácil acesso e edição manual do arquivo `data/planilhado.db`

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/thalesolm/Planilhado.git
cd Planilhado
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure a senha de administrador:
   - **Opção 1 (Recomendado)**: Criar um arquivo `.streamlit/secrets.toml` com:
     ```toml
     SENHA_ADMIN = "quemhackearegay666"
     ```
   - **Opção 2**: Definir uma variável de ambiente:
     - Windows (PowerShell): `$env:SENHA_ADMIN="quemhackearegay666"`
     - Linux/Mac: `export SENHA_ADMIN="quemhackearegay666"`
   - **Nota**: Se nenhuma das opções acima for configurada, a senha padrão será `quemhackearegay666`

4. Execute o aplicativo:
```bash
streamlit run app.py
```

O aplicativo será aberto automaticamente no navegador em `http://localhost:8501`

## ☁️ Deploy no Streamlit Community Cloud

### Passo a Passo

1. **Certifique-se de que o código está no GitHub**
   - Faça commit e push de todos os arquivos
   - O repositório deve estar público (para plano gratuito)

2. **Acesse o Streamlit Cloud**
   - Vá para [share.streamlit.io](https://share.streamlit.io)
   - Faça login com sua conta GitHub

3. **Crie um novo app**
   - Clique em "New app"
   - Selecione o repositório `Planilhado`
   - Selecione o branch `main` (ou o branch desejado)
   - O arquivo principal deve ser `app.py`
   - Clique em "Deploy!"

4. **Configure a senha de administrador (OBRIGATÓRIO)**
   - Após criar o app, vá em "⚙️ Settings" (ícone de engrenagem) → "Secrets"
   - No campo de texto, adicione EXATAMENTE:
     ```toml
     SENHA_ADMIN = "quemhackearegay666"
     ```
   - **IMPORTANTE**: No Streamlit Cloud, o arquivo `.streamlit/secrets.toml` local NÃO é usado!
   - Você DEVE configurar os secrets através da interface web do Streamlit Cloud
   - Salve e o app será reiniciado automaticamente
   - Após salvar, aguarde alguns segundos e tente fazer login novamente

5. **Aguarde o deploy**
   - O Streamlit Cloud irá instalar as dependências do `requirements.txt`
   - O banco de dados SQLite será criado automaticamente na pasta `data/`
   - O app estará disponível em uma URL como: `https://planilhado.streamlit.app`

### Importante para o Deploy

- ✅ O arquivo `requirements.txt` está configurado corretamente
- ✅ O arquivo `app.py` é o ponto de entrada do aplicativo
- ✅ A pasta `data/` será criada automaticamente quando o app rodar
- ✅ O banco de dados SQLite será persistente entre sessões no cloud
- ✅ **Configure a senha de administrador nos Secrets do Streamlit Cloud**

## 📝 Como Usar

### Controle de Acesso

- **Visualização**: Qualquer pessoa que acessar o link pode visualizar o planilhado
- **Edição**: Apenas usuários autenticados podem adicionar novas hunts
- Para editar, é necessário inserir a senha de administrador na barra lateral

### Cadastrar uma Nova Hunt

1. **Autentique-se** (se ainda não estiver):
   - Na barra lateral, digite a senha de administrador
   - Clique em "Entrar"

2. No formulário na barra lateral:
   - **Respawn**: Selecione um respawn existente ou escolha "Novo respawn" para digitar um novo
   - **Horários**: Defina o horário inicial e final da hunt
   - **Integrantes**: Preencha os nomes dos integrantes (campos opcionais)
   
3. Clique em "Salvar Hunt"

4. O sistema irá:
   - Validar se o horário final é maior que o inicial
   - Verificar se há conflito de horário com outras hunts do mesmo respawn
   - Salvar a hunt se tudo estiver válido

### Visualizar o Planilhado

- A área principal mostra todos os respawns cadastrados
- Cada respawn aparece em um quadro expansível com:
  - Horários de início e fim
  - Lista de integrantes
- Os quadros são ordenados alfabeticamente por respawn
- As hunts dentro de cada respawn são ordenadas por horário

## 🗄️ Banco de Dados

O banco de dados SQLite está localizado em `data/planilhado.db`.

### Estrutura da Tabela `hunts`

- `id`: Identificador único (auto-incremento)
- `respawn`: Nome do respawn (TEXT, obrigatório)
- `horario_inicio`: Horário de início no formato HH:MM (TEXT, obrigatório)
- `horario_fim`: Horário de fim no formato HH:MM (TEXT, obrigatório)
- `integrante1` a `integrante5`: Nomes dos integrantes (TEXT, opcional)
- `data_cadastro`: Data e hora do cadastro (TEXT, automático)

### Edição Manual

Você pode editar o banco de dados manualmente usando:
- **DB Browser for SQLite** (recomendado): [sqlitebrowser.org](https://sqlitebrowser.org/)
- **SQLite CLI**: Ferramenta de linha de comando
- Qualquer outro cliente SQLite

⚠️ **Atenção**: Faça backup antes de editar manualmente!

## 🛠️ Estrutura do Projeto

```
Planilhado/
├── app.py                 # Aplicativo principal Streamlit
├── database.py            # Funções de banco de dados (SQLite)
├── validators.py          # Validação de overlaps e regras de negócio
├── visualizations.py      # Funções para gerar os quadros de visualização
├── requirements.txt       # Dependências do projeto
├── .streamlit/
│   ├── config.toml        # Configurações do Streamlit (tema dark)
│   └── secrets.toml.example  # Exemplo de arquivo de secrets
├── data/
│   └── planilhado.db      # Banco de dados SQLite (criado automaticamente)
└── README.md              # Este arquivo
```

## 📦 Dependências

- `streamlit>=1.28.0`: Framework web para a interface
- `pandas>=2.0.0`: Manipulação de dados e visualizações

## 🔧 Tecnologias Utilizadas

- **Streamlit**: Framework web Python
- **SQLite**: Banco de dados local
- **Pandas**: Manipulação e visualização de dados

## 📄 Licença

Este projeto é de uso pessoal.

## 👤 Autor

Thales Machado
