# SLFN Business OS (HighLevel Clone)

An open-source, AI-powered business operating system - a FOSS alternative to HighLevel.

## Overview

This project replicates the core functionality of HighLevel (https://www.gohighlevel.com) using entirely open-source software. Built for the SLFN band community with local AI capabilities.

## Features

### Phase 1: Core CRM & Capture
- Contact management with custom fields
- Pipeline/deal management
- Form builder for lead capture
- Appointment scheduling

### Phase 2: Communication
- Chat widget with AI assistance
- Voice AI calling
- Social messaging integration

### Phase 3: Marketing Automation
- Email/SMS sequences
- Funnel builder
- Review management

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Auth**: JWT/OAuth2
- **Real-time**: WebSocket

### Frontend
- **Framework**: React + TypeScript
- **Styling**: TailwindCSS
- **State**: Zustand
- **Build**: Vite

### AI Services
- **Models**: Qwen2.5-Coder-1.5B (1.1GB)
- **Inference**: Ollama
- **Integration**: Local API

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (v2)
- **Storage**: MinIO (S3-compatible)

## Project Structure

```
slfn-business-os/
├── backend/
│   ├── app/                # API endpoints
│   ├── migrations/         # Database migrations
│   ├── tests/              # Test files
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── infrastructure/
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs/
│   ├── PRD.md              # Product Requirements
│   ├── ARCHITECTURE.md     # System design
│   ├── QUICKSTART.md       # Quick start guide
│   ├── ISSUES.md           # Issue tracker
│   └── VERIFICATION.md     # This file
├── .env.example
├── LICENSE                  # MIT License
└── README.md
```

## Getting Started

### Prerequisites
- Docker + Docker Compose v2
- Python 3.12+
- Node.js 18+
- Make (optional)

### Quick Start (Docker)

```bash
# Navigate to project
cd slfn-business-os

# Start all services (Docker Compose v2 uses 'docker compose')
docker compose up -d

# Wait for database to be ready (30-60 seconds)

# Run database migrations
docker compose exec backend python -m alembic upgrade head

# Access the application
# Frontend: http://localhost:3002
# Backend API: http://localhost:8081
# API Docs: http://localhost:8081/docs
# Nginx: http://localhost:8082
```

### Development Setup (Local)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://slfn:***@localhost:5432/slfn_business_os
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8081
VITE_WS_URL=ws://localhost:8081/ws
```

## API Documentation

Visit http://localhost:8081/docs when running locally for interactive API documentation.

## Ports Reference

| Service | Container Port | Host Port |
|---------|---------------|-----------|
| Backend | 8000 | 8081 |
| Frontend | 3000 | 3002 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| MinIO API | 9000 | 9002 |
| MinIO Console | 9001 | 9003 |
| Nginx | 80 | 8082 |

**Note**: Ports remapped to avoid conflicts:
- Backend 8081: Avoids llama-server (8000) and SLFN Nexus AI (8102/8103)
- Frontend 3002: Avoids conflicts with other services
- MinIO 9002/9003: Avoids conflicts

## Contributing

This is a FOSS project under MIT license. Contributions welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See LICENSE file for details.

## Acknowledgements

- Inspired by HighLevel (https://www.gohighlevel.com)
- Built with FastAPI, React, and other FOSS tools
- AI models from HuggingFace (Apache 2.0)

## Roadmap

See docs/ISSUES.md for the full roadmap and sprint planning.