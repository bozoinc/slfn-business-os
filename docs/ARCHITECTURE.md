# SLFN Nexus Platform - Architecture

## System Overview

The SLFN Nexus Platform is an open-source alternative to HighLevel, designed as a modular, scalable business operating system.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX Reverse Proxy                       │
│                              (:80)                                │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │      │   Backend    │      │   AI Service │
│  (React)     │      │  (FastAPI)   │      │  (Ollama)    │
│  :3000       │      │  :8000       │      │  :11434      │
└──────────────┘      └──────────────┘      └──────────────┘
        │                       │                       │
        │              ┌────────┴────────┐              │
        │              │                 │              │
        ▼              ▼                 ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   MinIO      │ │   PostgreSQL │ │     Redis    │ │   Redis      │
│  (S3 Storage)│ │   (:5432)    │ │   (:6379)    │ │   Cache      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Component Breakdown

### 1. Frontend (Port 3000)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **UI Library**: Custom components with Lucide icons

### 2. Backend API (Port 8000)
- **Framework**: FastAPI
- **Python Version**: 3.12
- **Database ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Authentication**: JWT tokens via python-jose
- **Validation**: Pydantic v2

### 3. AI Service (Port 11434)
- **Service**: Ollama
- **Models**: Qwen2.5-Coder-1.5B (primary), Qwen3-4B (secondary)
- **Inference**: Local CPU inference
- **API**: REST endpoints for model interaction

### 4. Storage (Port 9000/9001)
- **Service**: MinIO
- **Purpose**: S3-compatible object storage
- **Use Cases**: File uploads, form submissions, backups

### 5. Database (Port 5432)
- **Engine**: PostgreSQL 15
- **Extensions**: TimescaleDB (for time-series data)
- **Migrations**: Alembic
- **Connection Pool**: SQLAlchemy pool

### 6. Cache (Port 6379)
- **Service**: Redis 7
- **Purpose**: Session storage, caching, rate limiting

## Data Models

### Contact
```
contacts
├── id (UUID)
├── first_name, last_name
├── email, phone
├── company, job_title
├── address details
├── custom_fields (JSON)
├── created_at, updated_at
└── is_active
```

### Pipeline & Deal
```
pipelines
├── id, name, organization_id
├── is_active
└── stages (1..N)

stages
├── id, name, position
├── probability
└── pipeline_id (FK)

deals
├── id, title, value
├── stage_id (FK)
├── pipeline_id (FK)
├── contact_id (FK)
├── probability
├── closed_at, is_won
└── created_at, updated_at
```

### Forms
```
forms
├── id, name, description
├── is_active
├── fields (JSON)
├── settings (JSON)
├── embed_code
└── submissions_count

form_submissions
├── id, form_id (FK)
├── contact_id (FK)
├── data (JSON)
├── source, ip_address
└── created_at
```

## API Design

### RESTful Principles
- **Base URL**: `/api/v1/`
- **Versioning**: URL-based (`/api/v1/contacts`)
- **Content-Type**: `application/json`
- **Authentication**: Bearer token (JWT)

### Endpoints

#### Contacts
- `GET /contacts` - List contacts (paginated)
- `POST /contacts` - Create contact
- `GET /contacts/{id}` - Get specific contact
- `PUT /contacts/{id}` - Update contact
- `DELETE /contacts/{id}` - Delete contact
- `POST /contacts/{id}/tags` - Add tag to contact

#### Deals
- `GET /deals` - List deals (filterable)
- `POST /deals` - Create deal
- `GET /deals/{id}` - Get specific deal
- `PUT /deals/{id}` - Update deal
- `DELETE /deals/{id}` - Delete deal
- `POST /deals/{id}/close` - Close deal

#### Forms
- `GET /forms` - List forms
- `POST /forms` - Create form
- `GET /forms/{id}` - Get specific form
- `PUT /forms/{id}` - Update form
- `DELETE /forms/{id}` - Delete form
- `POST /forms/{id}/submit` - Submit form (public)

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based access control (future)
3. **Input Validation**: Pydantic models for all requests
4. **Database Security**: Parameterized queries only
5. **CORS**: Configured for known origins only
6. **Rate Limiting**: Redis-based (future)

## Performance Optimization

1. **Database Indexing**: 
   - Email on contacts (unique)
   - Names on contacts (search)
   - Form ID on submissions

2. **Caching**:
   - Redis for session storage
   - Redis for API response caching (future)

3. **Connection Pooling**:
   - SQLAlchemy connection pool
   - Redis connection pool

4. **Query Optimization**:
   - Lazy loading for relationships
   - Eager loading for frequently accessed data

## Deployment Architecture

### Local Development
```bash
docker-compose up -d
```

### Production Considerations
- Use separate containers per service
- Enable HTTPS via Let's Encrypt
- Use external PostgreSQL (managed)
- Use external Redis (managed)
- Use cloud storage (S3-compatible)
- CI/CD via GitHub Actions

## Monitoring & Observability

### Health Checks
- Backend: `/api/v1/health`
- Database: PostgreSQL health check
- Redis: PING command

### Metrics (Future)
- Request latency
- Error rates
- Database connection pool
- AI inference latency

## Scaling Strategy

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Read replicas for PostgreSQL
- Redis cluster for caching

### Vertical Scaling
- Increase container memory limits
- Optimize query performance
- Add more AI workers

## Future Enhancements

1. **Real-time Communication**: WebSocket for live chat
2. **AI Integration**: Local LLM for intelligent responses
3. **Email Service**: Self-hosted email (Mailu/Postfix)
4. **SMS Service**: Twilio-compatible gateway
5. **Webhook System**: Event-driven architecture
6. **Analytics Dashboard**: Business intelligence
7. **Mobile App**: React Native