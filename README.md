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
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis
- **Auth**: JWT/OAuth2
- **Real-time**: WebSocket

### Frontend
- **Framework**: React + TypeScript
- **Styling**: TailwindCSS
- **State**: Zustand
- **Build**: Vite

### AI Services
- **Models**: Qwen2.5-Coder-1.5B (1.1GB)
- **Inference**: llama.cpp / vLLM
- **Integration**: Local API

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: docker-compose
- **Storage**: MinIO (S3-compatible)

## Project Structure

```
highlevel-clone/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core services
│   │   ├── db/           # Database models
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── store/        # Zustand store
│   │   └── types/        # TypeScript types
│   ├── public/
│   └── Dockerfile
├── services/
│   └── ai/               # AI service scripts
├── infrastructure/
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs/
│   ├── PRD.md
│   ├── ISSUES.md
│   └── ARCHITECTURE.md
└── README.md
```

## Getting Started

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- Node.js 18+
- Make (optional)

### Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd highlevel-clone

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Development Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@db:5432/nexus
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key
ALGORITHMHS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## API Documentation

Visit http://localhost:8000/docs when running locally for interactive API documentation.

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