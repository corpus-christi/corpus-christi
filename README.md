# Corpus Christi

Corpus Christi (CC) is an open-source, internationalized church management suite developed at the [Center for Missions Computing](http://missionscomputing.org/) at [Taylor University](https://www.taylor.edu/).

CC helps churches manage their ministry operations across multiple languages and locales. It is built as a full-stack web application with a REST API backend and a Vue single-page application frontend.

---

## Modules

| Module | Description |
|--------|-------------|
| **People** | Member accounts, roles, and organizational hierarchies |
| **Groups** | Home church / small group management, meetings, and attendance |
| **Courses** | Training course catalog, offerings, enrollment, and diplomas |
| **Events** | Event planning with asset, team, and participant coordination |
| **Places** | Geographic locations, addresses, and areas |
| **Assets** | Resource tracking for events |
| **Teams** | Team management for event participation |

---

## Architecture

CC is a two-tier web application. The frontend and backend are developed and deployed independently, communicating over a JSON REST API.

```
Browser
  └── Vue 3 SPA (Vite dev server / static build)
        │  HTTP + JWT
        ▼
  FastAPI (uvicorn)
        │  SQLAlchemy 2
        ▼
  PostgreSQL
```

### Frontend (`ui/`)

A single-page application built with [Vue 3](https://vuejs.org/) and [Vuetify 3](https://vuetifyjs.com/).

| Concern | Technology |
|---------|-----------|
| Framework | Vue 3 (`<script setup lang="ts">`) |
| UI component library | Vuetify 3 |
| State management | [Pinia](https://pinia.vuejs.org/) |
| Routing | [Vue Router 4](https://router.vuejs.org/) |
| HTTP client | [Axios](https://axios-http.com/) (injected as `$http` / `$httpNoAuth`) |
| Internationalization | [vue-i18n 9](https://vue-i18n.intlify.dev/) |
| Build tool | [Vite](https://vitejs.dev/) |
| Package manager | [pnpm](https://pnpm.io/) |

The Vite dev server proxies all `/api` requests to `http://localhost:5000`.

### Backend (`api/`)

A REST API built with [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy 2](https://docs.sqlalchemy.org/).

| Concern | Technology |
|---------|-----------|
| Framework | FastAPI |
| Server | uvicorn |
| ORM | SQLAlchemy 2 (`Mapped[]`, `mapped_column()`) |
| Schema / validation | Pydantic v2 |
| Database migrations | Alembic |
| Authentication | JWT via `python-jose` + `OAuth2PasswordBearer` |
| Password hashing | passlib (bcrypt) |
| Email | fastapi-mail |
| CLI | [Typer](https://typer.tiangolo.com/) (`uv run cc-cli`) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Python | 3.13 |

Each module under `src/` follows the same structure:
- `__init__.py` — exports the `APIRouter`
- `api.py` — route handlers
- `models.py` — SQLAlchemy models + Pydantic schemas
- `test_*.py` — pytest tests

### Authentication

CC uses JSON Web Tokens (JWT):

1. The UI sends `username` + `password` to `POST /api/v1/auth/login`
2. The API validates credentials and returns a JWT
3. The UI stores the JWT in Pinia state and `localStorage`
4. All subsequent requests include `Authorization: Bearer <token>`
5. The API validates the token and checks it against the token blacklist on every protected request
6. On a 401 response, the UI clears the token and redirects to login

In Vue components:
- `inject('$http')` — authenticated requests
- `inject('$httpNoAuth')` — unauthenticated requests (login, public endpoints)

### Internationalization

CC is fully internationalized. No user-visible text is hardcoded.

Localization data lives in `ui/i18n/yaml/` as YAML keyed by dotted path then locale:

```yaml
person:
  name:
    first:
      en: First Name
      es: Nombre de pila
```

Compile to runtime JSON with `pnpm localize` (see [Common Commands](#ui)). In templates: `{{ $t('person.name.first') }}`; in `<script setup>`: `const { t } = useI18n()`.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [Node.js](https://nodejs.org/) | 18 LTS or later | UI runtime |
| [pnpm](https://pnpm.io/) | current | UI package manager |
| [uv](https://docs.astral.sh/uv/) | current | Python package manager |
| [Python](https://www.python.org/) | 3.13 | API runtime (managed by uv) |
| [PostgreSQL](https://www.postgresql.org/) | 14 or later | Database |

Windows users should use [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) or [Cygwin](https://www.cygwin.com/) for a bash shell. See [doc/postgres-windows.md](doc/postgres-windows.md) for Postgres on WSL.

---

## Development Setup

### 1. Clone

```bash
git clone https://github.com/corpus-christi/corpus-christi.git
cd corpus-christi
```

### 2. Set Up PostgreSQL

**Option A — Docker (recommended):**
```bash
cd api && docker-compose up --detach
```

**Option B — Local Postgres:**
```bash
createuser arco
createdb --owner=arco cc-dev
```
Other database names: `cc-test` (testing), `cc-staging`, `cc-prod`.

### 3. Configure the API

Copy the sample environment file and fill in your values:
```bash
cd api
cp .env.sample .env
```

Key variables:
```
PSQL_USER=arco
PSQL_PASS=password
PSQL_HOST=localhost
PSQL_DB=cc-dev
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-secret-key
CC_ENV=dev
```

Or set `DATABASE_URL` directly to override all `PSQL_*` vars:
```
DATABASE_URL=postgresql://arco:password@localhost/cc-dev
```

The `.env` file is in `.gitignore` — never commit it.

### 4. Install API Dependencies

Install [uv](https://docs.astral.sh/uv/) if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install all dependencies (uv manages the virtual environment automatically):
```bash
cd api
uv sync --extra dev
```

### 5. Initialize the Database

```bash
cd api
uv run alembic upgrade head
uv run cc-cli app load-all
```

Create a development account:
```bash
uv run cc-cli people new-account --first="Your" --last="Name" username password
```

### 6. Install UI Dependencies

```bash
cd ui
pnpm install
```

Install the [Vue DevTools](https://github.com/vuejs/vue-devtools) browser extension for Chrome/Firefox.

### 7. Run the Application

Open two terminals:

**Terminal 1 — API server:**
```bash
cd api
uv run uvicorn cc-api:app --reload --port 5000
```
Interactive API docs available at [http://localhost:5000/docs](http://localhost:5000/docs).

**Terminal 2 — UI dev server:**
```bash
cd ui
pnpm dev
```
Open the URL printed by Vite (typically [http://localhost:8080](http://localhost:8080)).

---

## Common Commands

### API

| Command | Description |
|---------|-------------|
| `uv run uvicorn cc-api:app --reload --port 5000` | Start dev server |
| `uv run pytest` | Run test suite |
| `uv run pytest -m smoke` | Run smoke tests only |
| `uv run alembic upgrade head` | Apply pending migrations |
| `uv run alembic revision --autogenerate -m "msg"` | Generate migration from model changes |
| `uv run cc-cli app load-all` | Load seed data |
| `uv run cc-cli app reset-db` | Drop and recreate all tables |
| `uv add <package>` | Add a dependency |

### UI

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start Vite dev server with HMR |
| `pnpm build` | Type-check and build for production |
| `pnpm preview` | Preview the production build |
| `pnpm test:unit` | Run unit tests with Vitest |
| `pnpm test:e2e` | Run end-to-end tests with Cypress |
| `pnpm lint` | Lint and auto-fix |
| `pnpm localize` | Regenerate `i18n/cc-i18n.json` from YAML sources |

---

## Project Structure

```
corpus-christi/
├── api/                    # FastAPI REST API (Python 3.13)
│   ├── src/                # Application source
│   │   ├── auth/           # Authentication and JWT
│   │   ├── people/         # People, roles, attributes
│   │   ├── places/         # Locations, countries, areas
│   │   ├── groups/         # Home groups and meetings
│   │   ├── courses/        # Courses, offerings, diplomas
│   │   ├── events/         # Events and coordination
│   │   ├── teams/          # Teams
│   │   ├── assets/         # Assets
│   │   ├── images/         # Image uploads
│   │   ├── emails/         # Email sending
│   │   ├── i18n/           # Translation data API
│   │   └── shared/         # Common utilities
│   ├── migrations/         # Alembic database migrations
│   ├── cc-api.py           # uvicorn entry point
│   ├── cli.py              # Typer CLI (cc-cli)
│   ├── config.py           # Pydantic Settings
│   ├── pyproject.toml      # Dependencies and project config
│   └── docker-compose.yaml # PostgreSQL container
│
├── ui/                     # Vue 3 single-page application
│   ├── i18n/               # Localization YAML sources + compiled JSON
│   ├── public/             # Static files served directly
│   └── src/
│       ├── components/     # Reusable UI components
│       ├── pages/          # Top-level route views
│       ├── stores/         # Pinia state (auth.ts)
│       ├── plugins/        # Plugin setup (Vuetify, i18n, Axios, Maps)
│       ├── router.ts       # Vue Router configuration
│       └── main.ts         # App entry point
│
├── doc/                    # Extended documentation
└── ansible/                # Deployment automation
```

---

## Visual Studio Code

Recommended extensions:
- `ms-python.python` — Python language support
- `charliermarsh.ruff` — Linter/formatter
- `Vue.volar` — Vue 3 language support

Point VS Code to the uv-managed interpreter:
```
api/.venv/bin/python
```

---

## Documentation

See the [`doc/`](doc/README.md) directory for:

- [`data-model.md`](doc/data-model.md) — Database schema
- [`testing.md`](doc/testing.md) — Testing approach and conventions
- [`coding.md`](doc/coding.md) — Code style and conventions
- [`tool-chain.md`](doc/tool-chain.md) — Tool chain details
- [`stories.md`](doc/stories.md) — User stories
- [`sdm.md`](doc/sdm.md) — Software development methodology

---

## Contributing

1. Fork the repository and create a feature branch
2. Follow the coding conventions in [`doc/coding.md`](doc/coding.md)
3. Write tests for new functionality
4. Submit a pull request against the `main` branch
