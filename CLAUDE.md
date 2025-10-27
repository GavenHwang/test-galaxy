# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend (Vue 3 + Vite + Element Plus)
**Package Manager: Must use pnpm** (project recently migrated from npm/yarn)
```bash
cd frontend
pnpm install        # Install dependencies
pnpm dev           # Start dev server on http://localhost:5173
pnpm build         # Build for production
pnpm preview       # Preview production build
```

### Backend (FastAPI + Tortoise ORM)
```bash
cd backend
python -m venv venv                # Create virtual environment
source venv/bin/activate          # Activate (Linux/Mac)
# venv\Scripts\activate           # Activate (Windows)
pip install -r requirements.txt   # Install dependencies

# Database setup (if needed)
aerich init-db                    # Initialize database
aerich migrate                    # Apply migrations

# Start development server
python run.py                     # Runs on http://localhost:9998 with auto-reload
```

### Production Deployment
```bash
# Frontend
cd frontend && pnpm build

# Backend
uvicorn app:app --host 0.0.0.0 --port 9998 --workers 4
```

## Architecture Overview

This is a full-stack environment management and version monitoring platform called **Galaxy Platform**.

### Technology Stack
- **Frontend**: Vue 3 (Composition API) + Vite + Element Plus + Pinia + Vue Router 4
- **Backend**: FastAPI + Tortoise ORM (async) + MySQL + Aerich (migrations)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Background Tasks**: APScheduler for periodic version checking (every 20 minutes)
- **Package Management**: **pnpm** (mandatory), no npm/yarn

### Core Domain Model
The system manages **multiple projects** (Scnet, GeneralMarket, GridView), each containing:
- **Environments**: Deployment environments with domain configurations
- **Components**: Individual software components within projects
- **Component Versions**: Automated version tracking across environments with history

### Key Architectural Patterns
- **Full Async/await**: Backend uses async throughout (FastAPI + Tortoise + aiohttp)
- **Role-based Authorization**: Hierarchical menu access control with JWT middleware
- **Scheduled Background Tasks**: Automatic version fetching from `/component/version.html` endpoints
- **Version Flag System**: `flag=1` for current versions, `flag=0` for historical
- **OS-specific Database Config**: Different MySQL configs for Linux/macOS/Windows in `app/settings/config.py`

### Database Configuration by OS
- **Linux**: MySQL on 10.0.36.102:3309
- **macOS**: MySQL on 10.0.16.49:3309
- **Windows**: MySQL on 127.0.0.1:3306
- **Default**: localhost:3306 (fallback)

## Important Development Constraints

### Package Management (CRITICAL)
- **MUST use pnpm** for frontend - project recently migrated as per git history
- Do not use npm or yarn under any circumstances
- Team members without pnpm: `npm install -g pnpm` or `curl -fsSL https://get.pnpm.io/install.sh | sh`

### Default Credentials
- **Username**: `admin`
- **Password**: `111111aA`
- **Note**: Admin user cannot be deleted or password reset

### Key Files to Understand
- `frontend/src/views/Env/VersionInfo.vue`: Main version monitoring interface with search, pagination, cascading environment selection
- `backend/app/core/init_app.py`: Application initialization and data seeding
- `backend/app/settings/config.py`: OS-specific database configuration
- `frontend/src/config/index.js`: API endpoint configuration

### Data Flow Architecture
1. **Authentication Flow**: JWT login → token storage → middleware validation → user context attachment
2. **Version Monitoring**: Scheduled tasks fetch from URLs → parse versions → compare with stored → create new version records if changed
3. **Environment Hierarchy**: Project → Environment → Component → ComponentVersion (with flag-based current/history)

### Background Task System
- **Schedule**: Every 20 minutes for Scnet project components
- **Method**: Concurrent HTTP requests to component version endpoints
- **Logic**: Parse version HTML, compare with database, create new records when versions change
- **Error Handling**: Timeout protection and comprehensive logging

## API Structure
- **Authentication**: `/api/login`, `/api/logout`
- **User Management**: `/api/user/*`
- **Environment Management**: `/api/env/*` (projects, environments, versions, comparisons)
- **Auto-generated Docs**: Available at `http://localhost:9998/docs` (FastAPI OpenAPI)

## Frontend Application Structure
- **Main Layout**: `Main.vue` with sidebar navigation and header
- **Environment Views**: `EnvInfo.vue`, `VersionInfo.vue`, `Compare.vue`, `EnvDetail.vue`, `EnvHistory.vue`
- **Key Features**: Cascading project-environment selection, real-time refresh, search/filtering, pagination
- **Navigation**: Role-based menu access control

## Development Notes
- **No Testing Framework**: Currently no automated tests configured
- **No CI/CD**: No GitHub Actions or deployment automation
- **Development-focused**: Optimized for local development with hot reload
- **Database Migrations**: Use Aerich for schema changes
- **Code Formatting**: Backend includes Black and isort in requirements