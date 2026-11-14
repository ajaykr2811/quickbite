# QuickBite API 🍛

A food-delivery backend built with **FastAPI**, grown one production feature at a time.
Restaurants, menus and orders today; auth, caching, queues, real-time tracking and more on the roadmap.

> Status: **M1 complete** · in-memory storage (a real database arrives in M3)

## Features
- Full CRUD for restaurants (`POST`, `GET`, `PATCH`, `DELETE`)
- Menus as a nested resource: `/restaurants/{id}/menu`, with a `veg_only` filter
- **Soft close / reopen** via `PATCH {"operational": false}`: closed restaurants disappear from listings and reject new menu items (`409 Conflict`), but keep their data
- Filtering by city and cuisine, plus a bounded `limit` (1–100)
- Request validation with Pydantic (bad input → `422`), interactive docs at `/docs`
- Hard delete cascades to the restaurant's menu items

## Tech stack
Python 3.11 · FastAPI · Pydantic v2 · Uvicorn

## Run it locally
```bash
git clone https://github.com/ajaykr2811/quickbite.git
cd quickbite
python3.11 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
fastapi dev app/main.py
```
Open http://127.0.0.1:8000/docs

## API
| Method | Path | Description | Success |
|---|---|---|---|
| GET | `/health` | Liveness check | 200 |
| POST | `/restaurants` | Create a restaurant | 201 |
| GET | `/restaurants?city=&cuisine=&limit=` | List open restaurants | 200 |
| GET | `/restaurants/{id}` | Get one restaurant | 200 |
| PATCH | `/restaurants/{id}` | Partial update (incl. close/reopen) | 200 |
| DELETE | `/restaurants/{id}` | Delete restaurant and its menu | 204 |
| POST | `/restaurants/{id}/menu` | Add a menu item | 201 |
| GET | `/restaurants/{id}/menu?veg_only=` | Get the menu | 200 |

## Design decisions
- **Soft close vs hard delete.** Closing is reversible and keeps history (future orders and reviews still point to the restaurant); `DELETE` is permanent.
- **Status codes mean something.** `404` = doesn't exist, `409` = exists but its current state forbids the action, `422` = invalid input.
- **PATCH only changes what you send.** Updates use `exclude_unset` + `exclude_none`, so omitted fields are never overwritten.
- **Guards live in endpoints, not shared helpers.** `get_restaurant_or_404` only finds; `ensure_operational` is applied only where a closed restaurant must be blocked, so the reopen path is never locked.

## Roadmap
- [x] M1 · CRUD for restaurants and menus
- [ ] M2 · Consistent error responses
- [ ] M3 · PostgreSQL with SQLAlchemy + Alembic
- [ ] M4 · Signup, login and JWT-protected routes
- [ ] Redis caching · message queue for orders · rate limiting · WebSocket order tracking
- [ ] Idempotent order creation · S3 image uploads · pagination · tests · Docker · CI
