# Formulário de visita às Ovitrampas

Site em **Python (Flask)** para registrar visitas às ovitrampas, com os dados gravados direto no **MongoDB**. Os registros podem ser criados, listados, editados e excluídos pelo próprio navegador.

## Funcionalidades

- Formulário com validação no navegador e no servidor (o servidor rejeita qualquer valor fora das opções).
- Cadastro completo (criar, listar, editar e excluir) ligado ao MongoDB via `pymongo`.
- **DS e bairro limitados à cidade do Recife:** o bairro é escolhido numa lista que depende do Distrito Sanitário selecionado (8 DS e 94 bairros).
- **5 ciclos** (Ciclo 1 a Ciclo 5).
- Campos separados para **nome** e **matrícula** do agente.
- Layout responsivo, com tema claro e escuro.
- Os campos ficam numa lista no `app.py`, então é fácil alterar o formulário.

## Campos

Todos são obrigatórios.

| Campo | Tipo |
|---|---|
| Ano | seletor de ano (grade de anos, como no calendário) |
| Ciclo | lista (Ciclo 1 a 5) |
| DS (Distrito Sanitário) | lista (DS I a DS VIII) |
| Bairro | lista (depende do DS) |
| Área do bairro | texto |
| Nome do agente | texto |
| Matrícula do agente | texto |
| Quantidade de palhetas/armadilhas | número |
| Id da Ovitrampa | texto |
| Data de Coleta | data |
| Data de entrega das palhetas | data |
| Observação | escolha única: F (Fechado), E (Extraviado), R (Recusado), D (Desocupado) ou Rec (Recuperada) |

> **Ruas:** o formulário não tem lista de ruas, porque são milhares e mudam com frequência. A "Área do bairro" continua sendo texto livre.

## Estrutura do projeto

```
.
├── app.py                    # servidor Flask, campos do formulário e ligação com o MongoDB
├── data/
│   └── recife_bairros.json   # DS -> bairros do Recife
├── index.html                # página do formulário (entregue pelo Flask)
├── teste_conexao.py          # testa a conexão com o MongoDB
├── requirements.txt
├── .env.example              # modelo das variáveis de ambiente
└── .gitignore
```

## Como rodar

### 1. Clonar e instalar

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar o MongoDB

Copie o modelo e edite:

```bash
cp .env.example .env             # Windows: copy .env.example .env
```

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=ovitrampas
COLLECTION=visitas
```

**Opção A: MongoDB Atlas (nuvem, plano gratuito M0)**

1. Crie uma conta em `mongodb.com/atlas` e crie um cluster **Free (M0)**.
2. Em **Database Access**, crie um usuário e uma senha (de preferência só letras e números).
3. Em **Network Access**, libere o seu IP (**Add Current IP Address**).
4. Em **Database → Connect → Drivers → Python**, copie a connection string e substitua `<password>` pela senha do usuário.
5. Cole no `.env`:
   ```env
   MONGO_URI=mongodb+srv://USUARIO:SENHA@cluster0.xxxxx.mongodb.net/
   ```

**Opção B: MongoDB local**

```bash
docker run -d --name mongo -p 27017:27017 -v mongo_dados:/data/db mongo:7
```

Mantenha `MONGO_URI=mongodb://localhost:27017`. Sem Docker, instale o MongoDB Community Server.

O banco e a coleção são criados automaticamente quando o primeiro registro é salvo.

### 3. Testar a conexão

```bash
python teste_conexao.py
```

### 4. Iniciar o site

```bash
python app.py
```

Abra `http://localhost:5000`. No topo deve aparecer **Conectado ao MongoDB**.

## API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/status` | confere a conexão com o MongoDB |
| GET | `/api/campos` | devolve a lista de campos do formulário |
| GET | `/api/registros` | lista os registros |
| POST | `/api/registros` | cria um registro |
| PUT | `/api/registros/<id>` | atualiza um registro |
| DELETE | `/api/registros/<id>` | exclui um registro |

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| Página sem campos e aviso "Não foi possível conectar ao servidor" | `python app.py` não está rodando | Ligue o servidor e recarregue a página |
| Aviso "Não foi possível acessar o MongoDB" | `MONGO_URI` errado ou IP não liberado no Atlas | Confira o `.env` e o **Network Access** |
| Página quebrada com `{ campos , tojson }` no código | Versão antiga do `index.html` (modelo Jinja) | Use o `index.html` novo desta versão |

## Personalizar

- **Campos:** edite a lista `CAMPOS` no `app.py`. O formulário e a tabela se ajustam sozinhos.
- **Bairros:** edite `data/recife_bairros.json`, no formato `"DS I": ["Bairro 1", "Bairro 2"]`.
- **Nomes dos bairros:** seguem a lista da Prefeitura do Recife. Se os seus dados usam outra grafia, ajuste o arquivo para manter tudo padronizado.

## Como o site se liga ao servidor

- O `index.html` **não tem os campos escritos nele**: ao abrir, ele pede a lista de campos ao servidor (`/api/campos`), que vem do `app.py`. Assim existe uma só fonte dos campos.
- No topo da página aparece **"Conectado ao MongoDB: banco / coleção"** quando tudo está certo. Se aparecer um aviso em vermelho, o servidor está desligado ou o `MONGO_URI` está errado.
- O jeito recomendado de abrir é `http://localhost:5000`. Abrir o arquivo `index.html` direto no navegador também funciona, **desde que o servidor esteja ligado** (`python app.py`).
- Os dados **sempre** vão para o MongoDB. A página não guarda nada no navegador.

## Publicar na internet (exemplo: Render)

1. Suba o projeto para o GitHub (sem o `.env`).
2. No Render, crie um **Web Service** a partir do repositório.
3. Comando de build: `pip install -r requirements.txt`
4. Comando de início: `gunicorn app:app`
5. Em **Environment**, cadastre `MONGO_URI`, `DB_NAME` e `COLLECTION`.
6. No Atlas, em **Network Access**, libere o acesso do servidor. O IP da hospedagem pode mudar; `0.0.0.0/0` funciona, mas é menos seguro, então use senha forte.

## Segurança

- Nunca suba o arquivo `.env` nem coloque a senha do banco no código.
- Esta versão **não tem login**. Se o site for publicado, qualquer pessoa com o link poderá ver, editar e excluir registros. Adicione autenticação antes de usar com dados reais.
- Use no MongoDB um usuário só para esta aplicação, com permissão mínima.

## Licença

Defina a licença do projeto antes de publicar (por exemplo, MIT) e adicione o arquivo `LICENSE`.
