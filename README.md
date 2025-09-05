# AI Communication Assistant

AI-Powered Communication Assistant for automated email support processing.

## Features

- Email retrieval from multiple providers (Gmail, Outlook, IMAP)
- AI-powered email categorization and prioritization
- Automated response generation using RAG and LLMs
- Dashboard for monitoring and managing support emails
- Analytics and reporting capabilities

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, PostgreSQL, Redis
- **AI/ML**: Google Gemini, Sentence Transformers, ChromaDB
- **Frontend**: React with TypeScript, Vite, Tailwind CSS
- **Infrastructure**: Docker, uv package manager

## Prerequisites

- Python 3.11+
- Node.js 18+
- uv package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- Docker (optional, for containerized development)

## Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-communication-assistant
   ```

2. **Install dependencies**
   ```bash
   # Install Python dependencies
   uv sync --dev
   
   # Install frontend dependencies
   cd frontend/dashboard
   npm install
   cd ../..
   ```

3. **Set up environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Add your API keys and database URLs
   ```

4. **Run database migrations**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start development servers**
   ```bash
   # Option 1: Use development script
   ./dev.sh  # Linux/Mac
   ./dev.bat # Windows
   
   # Option 2: Use Makefile
   make dev
   
   # Option 3: Start manually
   # Terminal 1 - Backend
   uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend
   cd frontend/dashboard
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Development

```bash
# Start all services with Docker
make docker-dev

# Or manually
docker-compose up --build
```

## Project Structure

```
ai-communication-assistant/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── core/               # Core configuration
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   └── main.py            # Application entry point
├── frontend/dashboard/      # React frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   └── package.json       # Dependencies
├── alembic/               # Database migrations
├── docker-compose.yml     # Development containers
├── docker-compose.prod.yml # Production containers
├── pyproject.toml         # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Environment Configuration

The application supports multiple environments:

- **Development**: `.env.development` - SQLite database, debug mode
- **Production**: `.env.production` - PostgreSQL database, optimized settings
- **Local**: `.env` - Your local configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/ai_comm_assistant

# AI Services
GEMINI_API_KEY=your_gemini_api_key_here

# Email Providers
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# Security
SECRET_KEY=your-secret-key-change-in-production
```

## Available Commands

```bash
# Development
make dev          # Start development servers
make install      # Install all dependencies
make test         # Run tests
make lint         # Run linting

# Docker
make docker-dev   # Start with Docker (development)
make docker-prod  # Start with Docker (production)

# Utilities
make build        # Build application
make clean        # Clean build artifacts
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Backend tests
uv run pytest

# Frontend tests
cd frontend/dashboard
npm run test

# Run all tests
make test
```

## Production Deployment

1. **Build production images**
   ```bash
   make docker-prod
   ```

2. **Configure production environment**
   ```bash
   cp .env.production .env
   # Edit with production values
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT