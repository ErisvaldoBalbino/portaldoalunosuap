# Portal do Aluno - SUAP

Sistema web que integra com a API do SUAP para fornecer uma interface amigável de visualização de notas, frequências e situação acadêmica dos alunos.

## 🌐 Site em Produção

Acesse o Portal do Aluno em: [https://portaldoalunosuap.vercel.app](https://portaldoalunosuap.vercel.app)

## 🚀 Funcionalidades

- 🔐 Login integrado com SUAP via OAuth2
- 📊 Dashboard com visão geral do desempenho acadêmico
- 📝 Visualização de notas e frequências por período
- 📈 Cálculo automático de notas necessárias para aprovação
- 📋 Relatório detalhado por disciplina
- 🎨 Interface moderna e responsiva

## 🛠️ Requisitos

- Python 3.8+
- Django 5.1+
- Outras dependências listadas em `requirements.txt`

## ⚙️ Configuração

1. Clone o repositório:
```bash
git clone https://github.com/ErisvaldoBalbino/portal-do-aluno-suap.git
cd portal-aluno
```

2. Crie e ative um ambiente virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
   - Renomeie o arquivo `.env.example` para `.env`
   - Preencha as variáveis com suas configurações:
```bash
# Django
SECRET_KEY="sua_chave_secreta_aqui"
DEBUG=True
ALLOWED_HOSTS="localhost,127.0.0.1"

# SUAP OAuth2
SUAP_CLIENT_ID="seu_client_id_aqui"
SUAP_CLIENT_SECRET="seu_client_secret_aqui"
SUAP_AUTH_URL="https://suap.ifrn.edu.br/o/authorize/"
SUAP_TOKEN_URL="https://suap.ifrn.edu.br/o/token/"
SUAP_API_URL="https://suap.ifrn.edu.br/api/"
```

5. Colete os arquivos estáticos:
```bash
python manage.py collectstatic
```

6. Execute as migrações:
```bash
python manage.py migrate
```

7. Inicie o servidor:
```bash
python manage.py runserver
```

8. Acesse o sistema:
   - Abra http://localhost:8000 no navegador
   - Você será redirecionado para o login do SUAP
   - Após autenticação, terá acesso ao dashboard

## 🔒 Segurança

- Autenticação via OAuth2 com SUAP
- Variáveis sensíveis protegidas em arquivo `.env`
- CSRF Protection ativada
- Sessões seguras
- Validação de dados de entrada


## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no GitHub.