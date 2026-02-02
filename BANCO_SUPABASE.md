# Instruções: banco no Supabase

## Streamlit Cloud: use o Connection pooler (porta 6543)

A conexão **direta** (porta 5432) costuma falhar no Streamlit Cloud com erro tipo *"Cannot assign requested address"*. Use o **Connection pooler** do Supabase:

1. No Supabase: **Project Settings** → **Database**.
2. Em **Connection string**, escolha **URI** e o modo **Transaction** (pooler).
3. A URL será algo como:  
   `postgresql://postgres.[PROJECT_REF]:[SENHA]@aws-0-[região].pooler.supabase.com:6543/postgres`
4. Nos Secrets do Streamlit Cloud, use **uma** das opções:

**Opção A – Uma única URL (recomendado)**  
Crie no Secrets:

```toml
DATABASE_URL = "postgresql://postgres.SEU_PROJECT_REF:SUA_SENHA@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

(Substitua `SEU_PROJECT_REF`, `SUA_SENHA` e a região pela URL que o Supabase mostrar.)

**Opção B – Formato [connections.postgresql]**  
Use o **host do pooler** e a porta **6543**:

```toml
[connections.postgresql]
host = "aws-0-us-east-1.pooler.supabase.com"
port = 6543
database = "postgres"
username = "postgres.SEU_PROJECT_REF"
password = "SUA_SENHA"
sslmode = "require"
```

(O `username` no pooler é `postgres` + ponto + o **Reference ID** do projeto, ex.: `postgres.skixkjbtqynxrsjtyjez`.)

### Se ainda não conectar: use só `DATABASE_URL`

Às vezes o formato `[connections.postgresql]` não é lido corretamente. Nesse caso use **apenas** a variável `DATABASE_URL`:

1. No Supabase: **Project Settings** → **Database** → **Connection string** → **URI** → modo **Transaction**.
2. Clique em **Copy** para copiar a URL completa.
3. Nos Secrets do Streamlit, **apague** o bloco `[connections.postgresql]` e deixe só:

```toml
DATABASE_URL = "cole_aqui_a_url_que_voce_copiou_do_supabase"
```

Exemplo (com sua região e projeto):

```toml
DATABASE_URL = "postgresql://postgres.skixkjbtqynxrsjtyjez:SUA_SENHA@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

**Importante:** o app codifica a senha automaticamente na URL. Se a senha tiver `#`, `!`, `^`, pode colar a URL com a senha em texto puro que a conexão será ajustada.

---

## Você precisa criar as tabelas manualmente?

**Não.** Assim que você configurar a `DATABASE_URL` nos Secrets do Streamlit Cloud (com a connection string do Supabase) e o app rodar, ele **cria as tabelas sozinho** na primeira execução (`CREATE TABLE IF NOT EXISTS`). Não é necessário fazer deploy de nada nem rodar SQL à mão no Supabase antes.

Se quiser criar (ou conferir) as tabelas manualmente no Supabase, use o que está abaixo.

---

## Onde rodar no Supabase

1. Acesse o [Supabase](https://supabase.com) e abra seu projeto.
2. No menu lateral: **SQL Editor**.
3. Cole o SQL abaixo e clique em **Run**.

---

## SQL para criar as tabelas (PostgreSQL)

```sql
-- Tabela de hunts (planilhado aprovado)
CREATE TABLE IF NOT EXISTS hunts (
    id SERIAL PRIMARY KEY,
    respawn VARCHAR(255) NOT NULL,
    horario_inicio VARCHAR(10) NOT NULL,
    horario_fim VARCHAR(10) NOT NULL,
    integrante1 VARCHAR(255),
    integrante2 VARCHAR(255),
    integrante3 VARCHAR(255),
    integrante4 VARCHAR(255),
    integrante5 VARCHAR(255),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de requisições pendentes (aguardando aprovação)
CREATE TABLE IF NOT EXISTS requisicoes (
    id SERIAL PRIMARY KEY,
    respawn VARCHAR(255) NOT NULL,
    horario_inicio VARCHAR(10) NOT NULL,
    horario_fim VARCHAR(10) NOT NULL,
    integrante1 VARCHAR(255),
    integrante2 VARCHAR(255),
    integrante3 VARCHAR(255),
    integrante4 VARCHAR(255),
    integrante5 VARCHAR(255),
    data_requisicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Colunas de cada tabela (referência)

### Tabela `hunts`

| Coluna          | Tipo         | Obrigatório | Descrição                          |
|-----------------|-------------|-------------|------------------------------------|
| `id`            | SERIAL      | sim (PK)    | Chave primária, gerada pelo banco  |
| `respawn`       | VARCHAR(255)| sim         | Nome do respawn                    |
| `horario_inicio`| VARCHAR(10) | sim         | Horário início (ex: 15:00)        |
| `horario_fim`   | VARCHAR(10) | sim         | Horário fim (ex: 18:00)           |
| `integrante1`   | VARCHAR(255)| não         | Nome do integrante 1               |
| `integrante2`   | VARCHAR(255)| não         | Nome do integrante 2               |
| `integrante3`   | VARCHAR(255)| não         | Nome do integrante 3               |
| `integrante4`   | VARCHAR(255)| não         | Nome do integrante 4               |
| `integrante5`   | VARCHAR(255)| não         | Nome do integrante 5               |
| `data_cadastro` | TIMESTAMP   | não         | Data/hora do cadastro (default: agora) |

### Tabela `requisicoes`

| Coluna           | Tipo         | Obrigatório | Descrição                          |
|------------------|-------------|-------------|------------------------------------|
| `id`             | SERIAL      | sim (PK)    | Chave primária, gerada pelo banco  |
| `respawn`        | VARCHAR(255)| sim         | Nome do respawn                    |
| `horario_inicio` | VARCHAR(10) | sim         | Horário início (ex: 15:00)        |
| `horario_fim`    | VARCHAR(10) | sim         | Horário fim (ex: 18:00)           |
| `integrante1`    | VARCHAR(255)| não         | Nome do integrante 1               |
| `integrante2`    | VARCHAR(255)| não         | Nome do integrante 2               |
| `integrante3`    | VARCHAR(255)| não         | Nome do integrante 3               |
| `integrante4`    | VARCHAR(255)| não         | Nome do integrante 4               |
| `integrante5`    | VARCHAR(255)| não         | Nome do integrante 5               |
| `data_requisicao`| TIMESTAMP   | não         | Data/hora da requisição (default: agora) |

---

## Resumo

1. Crie o projeto no Supabase e pegue a **connection string** (URI) do banco.
2. No Streamlit Cloud, em **Settings → Secrets**, adicione:
   ```toml
   DATABASE_URL = "postgresql://postgres.[ref]:[SENHA]@aws-0-[região].pooler.supabase.com:6543/postgres"
   ```
   (use a URI que o Supabase mostrar em **Project Settings → Database → Connection string → URI**.)
3. Não é obrigatório criar tabelas no Supabase antes: o app cria `hunts` e `requisicoes` na primeira vez que rodar com essa `DATABASE_URL`.
4. Se preferir, use o SQL acima no **SQL Editor** do Supabase para criar (ou conferir) as tabelas manualmente.
