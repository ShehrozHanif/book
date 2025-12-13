# Deployment Guide

This document describes how to deploy the AI-Native Physical AI & Humanoid Robotics Textbook.

## Architecture Overview

The system has two deployable components:

1. **Frontend (Docusaurus)** - Static site that can be deployed to any static hosting
2. **Backend (FastAPI)** - RAG API server that needs a Python runtime

For the hackathon demo, the backend can run locally while the frontend is deployed.

---

## Option 1: Local Development

### Frontend (Docusaurus)

```bash
cd docusaurus
npm install
npm start
```

This starts the development server at http://localhost:3000

### Backend (RAG API)

```bash
cd rag
pip install -r requirements.txt
python indexer.py  # Create the index first
python api.py      # Start the API server
```

This starts the API server at http://localhost:8000

---

## Option 2: GitHub Pages (Frontend Only)

### Automatic Deployment

1. Push to `main` or `master` branch
2. GitHub Actions will automatically build and deploy
3. Site will be available at `https://<username>.github.io/<repo-name>/`

### Manual Setup

1. Go to repository Settings → Pages
2. Set Source to "GitHub Actions"
3. Push changes to trigger deployment

### Configuration

Update `docusaurus.config.js`:

```javascript
const config = {
  url: 'https://<username>.github.io',
  baseUrl: '/<repo-name>/',
  organizationName: '<username>',
  projectName: '<repo-name>',
  // ...
};
```

---

## Option 3: Vercel (Recommended for Hackathon)

### One-Click Deploy

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Set the root directory to `docusaurus`
5. Click "Deploy"

### Configuration

The `vercel.json` file is already configured in the docusaurus directory.

---

## Option 4: Netlify

### Deploy Steps

1. Go to [netlify.com](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Connect to GitHub and select repository
4. Set build settings:
   - Base directory: `docusaurus`
   - Build command: `npm run build`
   - Publish directory: `docusaurus/build`
5. Click "Deploy site"

### Configuration

The `netlify.toml` file is already configured in the docusaurus directory.

---

## Backend Deployment Options

For a full deployment with the chatbot functional, you need to deploy the RAG API.

### Option A: Run Locally During Demo

```bash
cd rag
pip install -r requirements.txt
python indexer.py
uvicorn api:app --host 0.0.0.0 --port 8000
```

Update the frontend API URL in `src/components/ChatBot/index.js` if needed.

### Option B: Deploy to Railway/Render

1. Create a new web service
2. Connect to your GitHub repository
3. Set root directory to `rag`
4. Set start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Deploy

### Option C: Docker Deployment

Create `rag/Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python indexer.py
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Environment Variables

### Frontend

- `NODE_ENV` - Set to `production` for production builds

### Backend

- `PORT` - Port to run the API server (default: 8000)
- `INDEX_PATH` - Path to the index file (default: `./index.json`)

---

## Pre-Deployment Checklist

- [ ] Run `npm run build` in docusaurus directory - should complete without errors
- [ ] Run `python indexer.py` in rag directory - should create index.json
- [ ] Test API with `python api.py` - should start without errors
- [ ] Verify chatbot connects to API locally
- [ ] Update API URL in ChatBot component for production

---

## Troubleshooting

### Build Fails

- Check Node.js version (requires 18+)
- Delete `node_modules` and `package-lock.json`, then run `npm install`

### Chatbot Not Connecting

- Ensure RAG API is running
- Check CORS settings in `api.py`
- Verify API URL in ChatBot component

### Index Not Found

- Run `python indexer.py` before starting the API
- Check that chapter files have approval markers

---

## Quick Start Commands

```bash
# Frontend
cd docusaurus && npm install && npm run build

# Backend
cd rag && pip install -r requirements.txt && python indexer.py && python api.py

# Both (in separate terminals)
# Terminal 1: cd docusaurus && npm start
# Terminal 2: cd rag && python api.py
```
