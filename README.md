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
- **Frontend**: React with TypeScript
- **Infrastructure**: Docker, uv package manager

## Setup

1. Clone the repository
2. Install dependencies with `uv sync`
3. Set up environment variables in `.env`
4. Run database migrations with `alembic upgrade head`
5. Start the development server with `uv run dev`

## License

MIT