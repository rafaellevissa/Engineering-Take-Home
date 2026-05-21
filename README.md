# ---- Challenge API

Debt collection account management API.

## Live API

**URL:** http://3.80.160.210:8000/

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/accounts/` | List accounts with filters |
| POST | `/accounts/upload/` | CSV upload |

## Available Filters for `/accounts/`

| Parameter | Description |
|-----------|-------------|
| `min_balance` | Minimum balance (inclusive) |
| `max_balance` | Maximum balance (inclusive) |
| `consumer_name` | Search by name (partial, case-insensitive) |
| `status` | Account status: `INACTIVE`, `IN_COLLECTION`, `PAID_IN_FULL` |

## Examples

```bash
# Health check
curl http://3.80.160.210:8000/

# List all accounts
curl http://3.80.160.210:8000/accounts/

# Filter by status
curl "http://3.80.160.210:8000/accounts/?status=in_collection"

# Filter by balance range
curl "http://3.80.160.210:8000/accounts/?min_balance=1000&max_balance=50000"

# Filter by consumer name
curl "http://3.80.160.210:8000/accounts/?consumer_name=john"

# Combining filters
curl "http://3.80.160.210:8000/accounts/?min_balance=100&max_balance=50000&status=in_collection&consumer_name=williams"
```

## Pagination

The API uses Page Number Pagination.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `page` | Page number | 1 |
| `page_size` | Items per page | 10 (max: 100) |

**Pros:**
- Simple to use and understand
- Allows jumping to specific pages
- Good for UIs with page numbers

**Cons:**
- Results may be inconsistent if data changes between requests
- Not ideal for very large datasets
- Page numbers can shift when items are added/removed

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Ingest CSV data
python manage.py ingest_csv ../consumers_balances.csv

# Run server
python manage.py runserver
```

## Docker

```bash
# Build and run
docker compose up --build

# Run migrations
docker compose exec web python manage.py migrate
```

## Tests

```bash
python manage.py test collection
```
