#!/bin/bash

# Development script for AI Communication Assistant

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "uv could not be found. Please install uv first: https://docs.astral.sh/uv/"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
uv sync

# Start backend in background
echo "Starting backend server..."
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &

# Start frontend
echo "Starting frontend..."
cd frontend/dashboard
npm install
npm run dev