# Corpus Christi

Corpus Christi (CC) is an open-source, internationalized church management suite developed at the [Center for Missions Computing](http://missionscomputing.org/) at [Taylor University](https://www.taylor.edu/).

## Overview

CC helps churches manage their ministry operations across multiple languages and locales. It is built as a full-stack web application with a REST API backend and a single-page frontend.

### Modules

| Module | Description |
|--------|-------------|
| **Groups** | Home church / small group management, meetings, and attendance |
| **Courses** | Training course catalog, offerings, enrollment, and diplomas |
| **Events** | Event planning with asset, team, and participant coordination |
| **People** | Member accounts, roles, and organizational hierarchies |
| **Places** | Geographic locations, addresses, and areas |
| **Assets** | Resource tracking for events |
| **Teams** | Team management for event participation |

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | [Vue 3](https://vuejs.org/) + [Vuetify 3](https://vuetifyjs.com/) + [Pinia](https://pinia.vuejs.org/) |
| Build | [Vite](https://vitejs.dev/) |
| i18n | [vue-i18n 9](https://vue-i18n.intlify.dev/) |
| Backend | [Flask](https://flask.palletsprojects.com/) (Python) |
| Database | [PostgreSQL](https://www.postgresql.org/) |
| Auth | JSON Web Tokens (JWT) |

---

## Prerequisites

- **Node.js** 18 LTS or later
- **pnpm** (`npm install -g pnpm`)
- **Python** 3.7–3.9
- **PostgreSQL** 12 or later
- **Bash** (Linux/macOS native; Windows users should use WSL or Cygwin)

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/corpus-christi/corpus-christi.git
cd corpus-christi
```

### 2. Set Up the Database

You can run PostgreSQL locally or via Docker.

**Option A — Docker (recommended):**
```bash
cd api
docker-compose up --detach
```
This starts a Postgres container pre-configured with the default credentials.

**Option B — Local PostgreSQL:**
```bash
createuser arco
createdb --owner=arco cc-dev
```

### 3. Set Up the API

```bash
cd api
python3 -m venv venv
source venv/bin/activate        # Windows: source venv/Scripts/activate
pip install -r requirements.txt
```

Configure your shell for Flask (activates the venv and sets `FLASK_APP`):
```bash
source ./bin/set-up-bash.sh
```

Initialize the database and load seed data:
```bash
flask db migrate
flask db upgrade
flask data load-all
```

Create a development account:
```bash
flask account new --first="Your" --last="Name" username password
```

### 4. Set Up the UI

```bash
cd ui
pnpm install
```

### 5. Run the Application

Open **two terminals** — one for each server.

**Terminal 1 — API server:**
```bash
cd api
source ./bin/set-up-bash.sh
./bin/run-dev-server.sh
```

**Terminal 2 — UI dev server:**
```bash
cd ui
pnpm dev
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

---

## Development

### UI Development

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start the Vite dev server with HMR |
| `pnpmbuild` | Type-check and build for production |
| `pnpmpreview` | Preview the production build locally |
| `pnpmtest:unit` | Run unit tests with Vitest |
| `pnpmtest:e2e` | Run end-to-end tests with Cypress |
| `pnpmlint` | Lint and auto-fix source files |
| `pnpmlocalize` | Regenerate `i18n/cc-i18n.json` from YAML source files |

The UI dev server proxies all `/api` requests to `http://localhost:5000` (the Flask API).

### API Development

| Command | Description |
|---------|-------------|
| `flask run` | Start the development API server |
| `pytest` | Run the full API test suite |
| `flask db upgrade` | Apply pending database migrations |
| `flask db migrate -m "message"` | Generate a new migration from model changes |
| `flask data load-all` | Load seed/fixture data into the database |

### Database Connection

By default CC connects to a local Postgres database. You can override this with environment variables:

```bash
export DEV_DB_URL="postgresql://USER:PASSWORD@HOST/DBNAME"
export TEST_DB_URL="postgresql://USER:PASSWORD@HOST/cc-test"
```

---

## Project Structure

```
corpus-christi/
├── api/                    # Flask REST API
│   ├── bin/                # Utility shell scripts
│   ├── migrations/         # Alembic database migrations
│   ├── src/                # API source modules
│   │   ├── auth/           # Authentication endpoints
│   │   ├── groups/         # Home groups module
│   │   ├── courses/        # Courses and offerings
│   │   ├── events/         # Event management
│   │   ├── people/         # People and accounts
│   │   ├── places/         # Locations and geography
│   │   ├── i18n/           # Internationalization data API
│   │   └── boilerplate/    # Code generation tool (boil.py)
│   ├── config.py           # Flask configuration
│   ├── requirements.txt    # Python dependencies
│   └── docker-compose.yaml # PostgreSQL container
│
├── ui/                     # Vue 3 single-page application
│   ├── i18n/               # Localization YAML source files + generated JSON
│   ├── public/             # Static assets served directly
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Top-level route views
│   │   ├── stores/         # Pinia state stores (auth.ts)
│   │   ├── plugins/        # Vue plugin setup (vuetify, i18n, axios, maps)
│   │   ├── models/         # TypeScript data models (Account, Locale)
│   │   ├── utils/          # Utility functions (date formatting, geocoding)
│   │   ├── router.ts       # Vue Router configuration
│   │   ├── main.ts         # Application entry point
│   │   └── App.vue         # Root component
│   ├── tests/
│   │   └── e2e/            # Cypress end-to-end tests
│   ├── vite.config.ts      # Vite + Vitest configuration
│   └── package.json        # Node dependencies and scripts
│
├── doc/                    # Extended documentation
└── ansible/                # Infrastructure/deployment automation
```

---

## Internationalization

CC is fully internationalized from the ground up. No user-visible text is hardcoded — everything goes through [vue-i18n](https://vue-i18n.intlify.dev/).

**In templates:**
```html
<span>{{ $t('person.name.first') }}</span>
```

**In `<script setup>`:**
```ts
const { t } = useI18n()
t('person.name.first')
```

Localization data lives in `ui/i18n/yaml/` as YAML files. After editing them, regenerate the compiled JSON:

```bash
cd ui
pnpm localize
```

The generated file `ui/i18n/cc-i18n.json` is what the app reads at runtime.

---

## Authentication

CC uses JSON Web Tokens (JWT). The flow:

1. User submits username and password on the login page
2. The API validates credentials and returns a JWT
3. The UI stores the JWT in Pinia state and `localStorage`
4. All authenticated API requests include the JWT as an `Authorization: Bearer <token>` header
5. On a 401 response, the UI clears the JWT and redirects to the login page

In components, use the provided axios instances:
- `inject('$http')` — authenticated requests (includes JWT header)
- `inject('$httpNoAuth')` — unauthenticated requests (login, public endpoints)

---

## Documentation

See the [`doc/`](doc/README.md) directory for extended documentation including:

- [`develop.md`](doc/develop.md) — Detailed development environment setup
- [`data-model.md`](doc/data-model.md) — Database schema and data model
- [`testing.md`](doc/testing.md) — Testing approach and conventions
- [`coding.md`](doc/coding.md) — Code style and conventions
- [`stories.md`](doc/stories.md) — User stories
- [`tool-chain.md`](doc/tool-chain.md) — Tool chain details

---

## Contributing

1. Fork the repository and create a feature branch
2. Follow the coding conventions in [`doc/coding.md`](doc/coding.md)
3. Write tests for new functionality
4. Submit a pull request against the `development` branch
