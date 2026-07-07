# Enterprise E-Commerce Application

An enterprise-grade e-commerce application built with Python (FastAPI), SQLite, and Vanilla web technologies.

## Admin Credentials

| Field    | Value   |
|----------|---------|
| Username | `admin` |
| Password | `admin` |

> These are the default credentials for the built-in admin account.
> They can be changed via the `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables (see `.env.example`).

## Approach & Decisions

- **Architecture:** Modular FastAPI application. The backend serves both the RESTful API endpoints and the static frontend assets, keeping the project fully self-contained.
- **Backend:**
  - **FastAPI** was chosen for its high performance, automatic OpenAPI documentation, and modern asynchronous capabilities.
  - **SQLAlchemy** is used as the ORM to interact with the database.
  - **Alembic** manages database schema migrations, run automatically on container startup via `entrypoint.sh`.
- **Database:** **SQLite** is used as the local database. It is lightweight, requires no separate server, and perfectly fits the requirement for a "local DB" that is easy to run anywhere.
- **Frontend:**
  - Built as a Single Page Application (SPA) using **Vanilla HTML/CSS/JS**.
  - A modern aesthetic design (glassmorphism, dark mode) is implemented entirely with Vanilla CSS to ensure maximum flexibility and adherence to the challenge requirements (no Tailwind CSS).
- **Authentication:** A username/password login form is presented to unauthenticated users. Upon successful login, the backend returns an admin session token which is stored in `localStorage` and sent as `X-Admin-Key` on protected requests. The Shop tab is publicly accessible; Admin and Orders tabs are gated behind login.
- **Containerization:** The application is Dockerized, allowing it to be easily spun up in any environment.
- **Security:** Row-level XSS detection in CSV import using `bleach`. Products with malformed or invalid fields are imported as draft rather than discarded, with an admin alert indicating attention is required.

## Alternatives Considered

- **Backend Framework:** Django was considered for its built-in admin panel, which could rapidly fulfil the CRUD requirements. However, FastAPI provides more flexibility and better aligns with building a clean, modern REST API that a custom SPA frontend consumes.
- **Database:** PostgreSQL was considered, but it would require managing an additional service container. SQLite keeps the setup incredibly simple for a local test while still demonstrating relational database concepts.
- **Frontend Framework:** React or Vue were considered for building the UI. However, for a single, self-contained project, Vanilla JS is sufficient, avoids heavy build steps (Webpack/Vite), and demonstrates strong core web development skills.

## Example CSV

- The example CSV file `products.csv` was downloaded/provided on: **July 3, 2026**.

## How to Run Locally

### Using Docker (Recommended)

1. Ensure you have Docker and Docker Compose installed.
2. Copy `.env.example` to `.env` and fill in your values (or use defaults):
   ```bash
   cp .env.example .env
   ```
3. In the root of the project, run:
   ```bash
   docker compose up --build
   ```
4. Open your browser and navigate to `http://localhost:8000`.
5. Sign in with **admin / admin** (or your configured credentials) to access the Admin and Orders tabs.

### Running Locally without Docker

1. Ensure you have Python 3.11+ installed.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply database migrations:
   ```bash
   alembic upgrade head
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Open your browser and navigate to `http://localhost:8000`.

### Running Tests

```bash
pytest
```

The test suite uses an **in-memory SQLite database** and sets `TESTING=true` automatically via `pytest.ini`. No manual environment setup is needed.

## Environment Variables

See `.env.example` for full documentation of all supported variables.

| Variable           | Default       | Description                                          |
|--------------------|---------------|------------------------------------------------------|
| `DATABASE_URL`     | (SQLite file) | SQLAlchemy database URL                              |
| `ADMIN_SECRET_KEY` | `changeme`    | Internal token sent as `X-Admin-Key` on API calls   |
| `ADMIN_USERNAME`   | `admin`       | Admin login username                                 |
| `ADMIN_PASSWORD`   | `admin`       | Admin login password                                 |
| `TESTING`          | *(unset)*     | **Injected by pytest only.** Do not set in `.env`.  |

### Note on `TESTING`

`TESTING=true` is set exclusively by `pytest.ini` and serves two purposes:
1. Prevents the FastAPI lifespan from seeding the database on startup (which would interfere with isolated test databases).
2. Enables the `GET /api/auth/hint` endpoint, which returns the current default admin credentials so the login modal can display a "Default credentials: admin / admin" tip to reviewers running the app locally.

**Do not set `TESTING=true` in a real deployment**, as it would suppress database seeding and expose the credentials hint endpoint.

## Features

- **Shop View:** Browse and search products, view real-time stock. Public access — no login required.
- **Purchase:** Simulate a purchase which deducts from inventory. Includes an auto-fill button for testing.
- **Admin View:** Complete CRUD for products and a CSV import tool. Requires login.
- **Order History:** Full audit trail of all checkout events, including product name, SKU, quantity, unit price at time of purchase, and timestamp. Requires login.
- **CSV Import:** Background-task import with real-time status polling. Invalid rows are imported as drafts rather than discarded; XSS attempts are rejected.
