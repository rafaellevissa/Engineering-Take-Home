# Aktos Challenge API

API para gerenciamento de contas de cobrança.

## Live API

**URL:** http://3.80.160.210:8000/

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Health check |
| GET | `/accounts/` | Lista contas com filtros |
| POST | `/accounts/upload/` | Upload de CSV |

## Filtros disponíveis em `/accounts/`

| Parâmetro | Descrição |
|-----------|-----------|
| `min_balance` | Valor mínimo (inclusivo) |
| `max_balance` | Valor máximo (inclusivo) |
| `consumer_name` | Busca por nome (parcial, case-insensitive) |
| `status` | Status da conta: `INACTIVE`, `IN_COLLECTION`, `PAID_IN_FULL` |

## Exemplos

```bash
# Health check
curl http://3.80.160.210:8000/

# Listar todas as contas
curl http://3.80.160.210:8000/accounts/

# Filtrar por status
curl "http://3.80.160.210:8000/accounts/?status=in_collection"

# Filtrar por range de balance
curl "http://3.80.160.210:8000/accounts/?min_balance=1000&max_balance=50000"

# Filtrar por nome do consumer
curl "http://3.80.160.210:8000/accounts/?consumer_name=john"

# Combinando filtros
curl "http://3.80.160.210:8000/accounts/?min_balance=100&max_balance=50000&status=in_collection&consumer_name=williams"
```

## Paginação

A API usa paginação por número de página (Page Number Pagination).

| Parâmetro | Descrição | Default |
|-----------|-----------|---------|
| `page` | Número da página | 1 |
| `page_size` | Itens por página | 10 (max: 100) |

**Prós:**
- Simples de usar e entender
- Permite saltar para páginas específicas
- Bom para UIs com números de página

**Contras:**
- Resultados podem ser inconsistentes se dados mudam entre requisições
- Não ideal para datasets muito grandes
- Números de página podem mudar quando itens são adicionados/removidos

## Desenvolvimento Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar migrations
python manage.py migrate

# Ingerir dados do CSV
python manage.py ingest_csv ../consumers_balances.csv

# Rodar servidor
python manage.py runserver
```

## Docker

```bash
# Build e run
docker compose up --build

# Rodar migrations
docker compose exec web python manage.py migrate
```

## Testes

```bash
python manage.py test collection
```
