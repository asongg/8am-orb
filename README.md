# 8AM ORB

A FastAPI backend for experimenting with systematic trading strategies, specifically a trading strategy I saw online called '8AM ORB'. The app stores market bars, runs backtests, tracks trades/equity/risk events, and includes Alpaca integrations for historical data and paper trading.

## The tech stack:

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

Update `.env` with your local database settings and Alpaca paper-trading creds

```bash
docker compose up --build
```

The API runs at `http://localhost:8000` by default

## Endpoints that are useful:

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
