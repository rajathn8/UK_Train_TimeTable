# UK Train Timetable API

A production-grade FastAPI application for UK train timetable journey planning, integrating with TransportAPI and using SQLite (SQLAlchemy) for caching and persistence.

## Features
- **Journey Planning API**: Find the earliest possible arrival time for a multi-leg UK train journey, given a list of station codes, start time, and maximum wait per leg.
- **TransportAPI Integration**: Fetches live and scheduled train data from TransportAPI, with robust error/status handling and caching.
- **Database Caching**: Uses SQLite and SQLAlchemy to cache timetable data, minimizing external API calls and improving performance.
- **RESTful Endpoints**: Clean, documented endpoints with OpenAPI schema and request/response validation.
- **Input Validation**: Pydantic schemas enforce correct station code formats, time formats, and wait limits.
- **Comprehensive Logging**: Info, debug, warning, and error logs throughout the app for observability and debugging.
- **Robust Error Handling**: All API/database errors are caught and returned with appropriate status codes and messages.
- **Testing**: Extensive unit and integration tests for all major logic, error scenarios, and API endpoints.
- **Production-Ready**: Type hints, docstrings, and code style (Black/Flake8) throughout. Dockerfile included.

## Quickstart
1. **Install dependencies**
   ```sh
   poetry install
   ```
2. **Set up environment variables** (or edit `src/app/settings.py`):
   - `app_id`, `app_key` (TransportAPI credentials)
   - `DB_URL` (default: SQLite)
3. **Run the app**
   ```sh
   PYTHONPATH=src poetry run python -m main
   ```
   The API will be available at http://localhost:8000

## API Endpoints
- `GET /health` — Health check and metadata
- `POST /v1/journey` — Plan a journey
  - **Request:**
    ```json
    {
      "station_codes": ["LBG", "SAJ", "NWX", "BXY"],
      "start_time": "2025-06-04T07:00:00+01:00",
      "max_wait": 15
    }
    ```
  - **Response:**
    ```json
    {
      "arrival_time": "2025-06-04T08:11:00+01:00"
    }
    ```

## Project Structure
- `src/app/uk_train_schedule/` — Main journey logic, models, CRUD, controller, and API router
- `src/app/health/` — Health check endpoint and schema
- `src/database/session.py` — Database session management
- `src/app/settings.py` — App settings and secrets
- `src/main.py` — Entrypoint
- `tests/` — Unit and integration tests (pytest + Behave BDD)

## Development
- **Lint:** `poetry run flake8 src/`
- **Format:** `poetry run black src/`
- **Test:** `poetry run pytest`

## Notes
- API keys are set in `src/app/settings.py` by default; override in production
- SQLite is default for local dev; use PostgreSQL for production
- See code comments and docstrings for further details

---
For more, see the code and OpenAPI docs at `/docs` when running the app.
