# trdr

A FastAPI backend for experimenting with systematic trading strategies. The app stores market bars, runs backtests, tracks trades/equity/risk events, and includes Alpaca integrations for historical data and paper trading.

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- Docker Compose
- Alpaca API support

## Setup

```bash
cp .env.example .env
```

Update `.env` with your local database settings and, optionally, Alpaca paper-trading credentials.

```bash
docker compose up --build
```

The API runs at `http://localhost:8000`.

## Useful Endpoints

- `GET /health`
- `GET /market/bars`
- `POST /backtests/run`
- `GET /backtests`
- `GET /backtests/{run_id}`
- `GET /backtests/{run_id}/trades`
- `GET /backtests/{run_id}/equity`
- `GET /backtests/{run_id}/risk-events`

## Development

Run database migrations from the backend container or a local backend environment:

```bash
alembic upgrade head
```

Secrets should stay in `.env`. Use `.env.example` only for safe placeholder values.
