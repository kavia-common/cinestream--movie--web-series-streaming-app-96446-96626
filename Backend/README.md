# CineStream Backend (FastAPI)

This is the CineStream backend service implemented with FastAPI and SQLAlchemy. It provides REST APIs for:
- Authentication (register/login)
- User profiles
- Content browsing and admin management
- Watchlist
- Subscriptions and (simulated) payments (Stripe / PayPal / UPI)
- Ratings & reviews
- Secure streaming URL issuance
- Admin analytics

## Running locally

1. Create a `.env` from `.env.example` and set your configuration.

   Important: Set CORS_ALLOW_ORIGINS to include your frontend origin(s). Examples:
   - For local dev: CORS_ALLOW_ORIGINS="http://localhost:4000,http://127.0.0.1:4000"
   - For Kavia preview (current): CORS_ALLOW_ORIGINS="https://vscode-internal-36075-beta.beta01.cloud.kavia.ai:4000"
   - Another preview example: CORS_ALLOW_ORIGINS="https://vscode-internal-14938-beta.beta01.cloud.kavia.ai:4000"

   Do not use "*" when credentials are included in requests, as browsers will block such responses. The backend is configured with FastAPI's CORSMiddleware to respond to preflight OPTIONS requests with the allowed methods and headers.

2. Install dependencies:
   pip install -r requirements.txt
3. Start the server:
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

By default, if `DATABASE_URL` is not provided the service will create a local `sqlite` database `dev.db` for development/documentation purposes only. For production, configure PostgreSQL via `DATABASE_URL`.

## Payments

Payments are simulated to avoid real gateway dependencies:
- Stripe tokens must start with `tok_`
- PayPal tokens must start with `pp_`
- UPI tokens must start with `upi_`

A successful simulation records a `Payment` with status `succeeded`.

## API Docs

OpenAPI docs available at `/docs` and `/redoc`. To export the OpenAPI schema, run:
python -m src.api.generate_openapi

## Authentication

Use OAuth2 password flow:
- Login at `/auth/login` with form fields `username` (email) and `password`
- Use `Authorization: Bearer <token>` for secured endpoints

## Admin

Mark a user as admin directly in the database (`users.is_admin = true`) to access admin endpoints.
