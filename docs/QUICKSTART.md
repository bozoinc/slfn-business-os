# Quick Start Guide

## Prerequisites

- Docker + Docker Compose
- Python 3.12+
- Node.js 18+
- Make (optional)

## Quick Start (Docker)

```bash
# Clone and navigate to project
cd highlevel-clone

# Start all services
docker-compose up -d

# Wait for services to start (30-60 seconds)
sleep 30

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Development Setup (Local)

### Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Create Contact
```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "email": "john@example.com"}'
```

### List Contacts
```bash
curl http://localhost:8000/api/v1/contacts
```

### Create Deal
```bash
curl -X POST http://localhost:8000/api/v1/deals \
  -H "Content-Type: application/json" \
  -d '{"title": "Website Redesign", "value": 5000000, "pipeline_id": "pipeline-1", "stage_id": "stage-1"}'
```

## Project Structure

```
highlevel-clone/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core configuration
│   │   ├── db/                # Database models & session
│   │   └── main.py            # Application entry point
│   ├── migrations/            # Alembic migrations
│   ├── tests/                 # Test files
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Docker image
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── hooks/             # Custom hooks
│   │   └── App.tsx            # Main application
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── infrastructure/           # Infrastructure files
│   ├── docker-compose.yml     # Docker Compose
│   └── nginx.conf           # Reverse proxy config
│
├── docs/                     # Documentation
│   ├── PRD.md               # Product Requirements Doc
│   ├── ARCHITECTURE.md      # System architecture
│   └── QUICKSTART.md        # This file
│
├── tests/                    # Integration tests
├── Makefile                 # Development commands
├── LICENSE                  # MIT License
└── README.md               # Project overview
```

## Common Commands

```bash
# Using Makefile
make up         # Start all services
make down       # Stop all services
make logs       # View logs
make db-migrate # Run migrations
make test       # Run tests
make clean      # Clean up containers and volumes

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose exec backend bash
docker-compose exec db psql -U hl_user -d hl_nexus
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U hl_user -d hl_nexus
```

### Backend Not Responding
```bash
# Check if backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Frontend Not Loading
```bash
# Check if frontend is running
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend

# Check if API is accessible
curl http://localhost:8000/api/v1/health
```

## Next Steps

1. Run the initial migration
2. Create a test contact
3. Build your first form
4. Set up your first pipeline
5. Explore the API documentation

## Support

- API Docs: http://localhost:8000/docs
- Open an issue for bugs or feature requests
- Check docs/ISSUES.md for roadmap