# UK Train Timetable API

A FastAPI-based service to fetch, store, and query UK train timetable data using the TransportAPI, with results cached in a SQLite database via SQLAlchemy.

## Features
- Fetches train timetable data from TransportAPI and caches it in SQLite
- REST API to find the earliest arrival time for a given route and start time
- Health check endpoint
- Modular, production-ready structure
- Secrets and settings managed via environment variables or `src/app/settings.py`

## Requirements
- Python 3.12+
- Poetry
- TransportAPI account (for `app_id` and `app_key`)

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```sh
   poetry install
   ```
3. **Set environment variables (optional):**
   - `app_id` and `app_key` for TransportAPI (defaults are set in `src/app/settings.py`)
   - `APP_ENV` (default: DEV)
   - `DB_URL` (default: sqlite:///train_schedule.db)
   - You can use a `.env` file or export variables in your shell.

4. **Run the app:**
   ```sh
   PYTHONPATH=src poetry run python -m main
   ```
   The API will be available at http://localhost:8000

## API Endpoints
- `GET /v1/health` — Health check
- `POST /v1/journey` — Find earliest journey
  - Request body:
    ```json
    {
      "station_codes": ["LBG", "SAJ", "NWX", "BXY"],
      "start_time": "2025-06-04T07:00:00+01:00",
      "max_wait": 15
    }
    ```
  - Response:
    ```json
    {
      "journey": [
        {"from": "LBG", "to": "SAJ", "departure": "2025-06-04T07:19:00+01:00", "arrival": "2025-06-04T07:28:00+01:00", "service_id": "..."},
        ...
      ],
      "arrival_time": "2025-06-04T08:11:00+01:00"
    }
    ```

## Development
- Lint: `poetry run flake8 src/`
- Format: `poetry run black src/`
- Test: `poetry run pytest`

## Project Structure
- `src/app/health/` — Health check endpoint
- `src/app/uk_train_schedule/` — Journey logic, models, and API
- `src/database/session.py` — Database session management
- `src/app/settings.py` — App settings and secrets
- `src/main.py` — App entrypoint

## Notes
- API keys are set in `src/app/settings.py` by default, but you should override them in production.
- The database is SQLite by default for easy local development.
- For production, consider using PostgreSQL and proper secret management.

---

For more details, see the code and comments in each module.
