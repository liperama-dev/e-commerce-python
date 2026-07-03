# Enterprise E-Commerce Application

An enterprise-grade e-commerce application built with Python (FastAPI), SQLite, and Vanilla web technologies.

## Approach & Decisions

- **Architecture:** Monolithic architecture. The FastAPI backend serves both the RESTful API endpoints and the static frontend assets. This simplifies deployment and keeps the project fully self-contained.
- **Backend:** 
  - **FastAPI** was chosen for its high performance, automatic OpenAPI documentation, and modern asynchronous capabilities.
  - **SQLAlchemy** is used as the ORM to interact with the database.
- **Database:** **SQLite** is used as the local database. It is lightweight, requires no separate server, and perfectly fits the requirement for a "local DB" that is easy to run anywhere.
- **Frontend:** 
  - Built as a Single Page Application (SPA) using **Vanilla HTML/CSS/JS**.
  - A modern aesthetic design (glassmorphism, dark mode) is implemented entirely with Vanilla CSS to ensure maximum flexibility and adherence to the challenge requirements (no Tailwind CSS).
- **Containerization:** The application is Dockerized, allowing it to be easily spun up in any environment.
- **Security:** Row-level security for csv import can detect malicious html or js in csv files with alerts to the user. Rows with malformed or invalid fields are imported as "draft". The admin panel will show an alert indicating that one or more products need attention and allow the admin to edit or delete the draft products.

## Alternatives Considered

- **Backend Framework:** Django was considered for its built-in admin panel, which could rapidly fulfill the CRUD requirements. However, FastAPI provides more flexibility and better aligns with building a clean, modern REST API that a custom SPA frontend consumes.
- **Database:** PostgreSQL was considered, but it would require managing an additional service container. SQLite keeps the setup incredibly simple for a local test while still demonstrating relational database concepts.
- **Frontend Framework:** React or Vue were considered for building the UI. However, for a single, self-contained project, Vanilla JS is sufficient, avoids heavy build steps (Webpack/Vite), and demonstrates strong core web development skills.

## Example CSV

- The example CSV file `products.csv` was downloaded/provided on: **July 3, 2026**.

## How to Run Locally

### Using Docker (Recommended)

1. Ensure you have Docker and Docker Compose installed.
2. In the root of the project, run:
   ```bash
   docker compose up --build
   ```
3. Open your browser and navigate to `http://localhost:8000`.

### Running Locally without Docker

1. Ensure you have Python 3.11+ installed.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
5. Open your browser and navigate to `http://localhost:8000`.

## Features
- **Shop View:** Browse and search products, view real-time stock.
- **Purchase:** Simulate a purchase which deducts from inventory. Includes an auto-fill button for testing.
- **Admin View:** Complete CRUD for products and a CSV import tool.
