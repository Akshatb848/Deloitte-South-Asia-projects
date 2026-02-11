# Education Intelligence Dashboard

**Ministry of Education, Government of India**
**Technology Partner: Deloitte Touche Tohmatsu**

---

## Overview

The Education Intelligence Dashboard is an AI-powered, government-grade analytics platform designed for the Ministry of Education. It transforms monthly newsletter data into an interactive, searchable intelligence command center suitable for cabinet-level presentations and international delegations.

### Key Features

- **Calendar-Based Navigation**: Timeline interface for month-wise data exploration
- **Interactive Statistical Dashboard**: Animated charts and real-time counters
- **AI-Powered Chatbot**: Conversational interface using open-source LLM (Mistral/Llama)
- **RAG System**: Semantic search with FAISS vector database
- **Comparative Analysis**: State and time-period comparisons
- **Query-to-Visualization**: Intelligent chart highlighting based on user queries
- **Government-Grade Design**: Professional, authoritative UI/UX
- **Conference-Ready**: Optimized for projector displays and official presentations

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Timeline  │  │  Dashboard   │  │   Chatbot    │        │
│  │   Widget   │  │   Charts     │  │     UI       │        │
│  └────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
                           │
                    REST API (FastAPI)
                           │
┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer                           │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │    RAG     │  │     LLM      │  │    Chat      │        │
│  │   System   │  │   Handler    │  │   Handler    │        │
│  │  (FAISS)   │  │  (Ollama)    │  │ (Orchestr.)  │        │
│  └────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Newsletter │  │    Vector    │  │   Embeddings │        │
│  │    JSON    │  │   Database   │  │    Cache     │        │
│  └────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **HTML5/CSS3**: Government-grade responsive design
- **JavaScript**: Vanilla ES6+ (no framework bloat)
- **Chart.js**: Statistical visualizations
- **Inter Font**: Professional typography

### Backend
- **FastAPI**: High-performance async API
- **Python 3.11+**: Modern Python features
- **Sentence Transformers**: Text embeddings
- **FAISS**: Vector similarity search
- **Ollama**: Local LLM inference

### LLM
- **Mistral 7B Instruct**: Recommended model
- **Llama 3 Instruct**: Alternative option
- **Local Inference**: No external API dependencies

### Infrastructure
- **Docker**: Containerized deployment
- **Nginx**: Frontend serving and reverse proxy
- **Docker Compose**: Orchestration

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- 8GB+ RAM (16GB recommended for LLM)
- 10GB+ disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Akshatb848/Deloitte-South-Asia-projects.git
   cd Deloitte-South-Asia-projects
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Pull LLM model**
   ```bash
   docker exec -it education-dashboard-ollama ollama pull mistral:7b-instruct
   ```

5. **Access the dashboard**
   - Frontend: http://localhost:8080
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Manual Setup (Without Docker)

### Backend Setup

**Requirements**: Python 3.10.11 (or Python 3.10.x)

1. **Create virtual environment**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Verify Python version
   python --version  # Should show Python 3.10.x
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama**
   ```bash
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # macOS
   brew install ollama

   # Windows
   # Download from https://ollama.com/download
   ```

4. **Pull LLM model**
   ```bash
   ollama pull mistral:7b-instruct
   ```

5. **Start Ollama server**
   ```bash
   ollama serve
   ```

6. **Start backend API**
   ```bash
   cd backend
   python main.py
   ```

### Frontend Setup

1. **Serve frontend**
   ```bash
   cd frontend
   python -m http.server 8080
   ```

2. **Access dashboard**
   - Open http://localhost:8080 in your browser

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LLM Configuration
LLM_MODEL=mistral:7b-instruct
OLLAMA_HOST=http://localhost:11434

# Vector Database
VECTOR_DB_PATH=./vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:8080"]

# Security
RATE_LIMIT_PER_MINUTE=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

## Usage Guide

### Dashboard Navigation

1. **Timeline Calendar**: Click on any month to view that period's data
2. **Statistics Cards**: Animated counters show key metrics
3. **Interactive Charts**: Hover for detailed tooltips
4. **AI Chatbot**: Click the chat button (bottom right) to start

### Chatbot Examples

**Factual Queries**
```
"What was the attendance rate in June 2025?"
"How many APAAR IDs were issued in August?"
"Show me teacher tracking progress"
```

**Comparisons**
```
"Compare Kerala and Gujarat attendance rates"
"Which state has the highest APAAR coverage?"
"Show me infrastructure growth from April to January"
```

**Trend Analysis**
```
"Show attendance growth graph"
"What's the trend in teacher tracking?"
"Has enrollment been increasing?"
```

**Policy Insights**
```
"Summarize dropout prevention impact"
"What are the infrastructure gaps?"
"Which initiatives were most successful?"
```

---

## API Documentation

### Endpoints

#### Health Check
```bash
GET /api/health
```

Returns system health status and component connectivity.

#### Chat
```bash
POST /api/chat
Content-Type: application/json

{
  "query": "What was the attendance rate in June?",
  "current_month": "June_2025",
  "include_visualization": true
}
```

#### Compare
```bash
POST /api/compare
Content-Type: application/json

{
  "entities": ["Kerala", "Gujarat"],
  "metric": "attendance",
  "months": ["June_2025"]
}
```

#### Semantic Search
```bash
POST /api/search?query=teacher%20training&top_k=5
```

---

## Data Management

### Adding New Newsletter Data

1. **Edit data file**
   ```bash
   nano data/newsletter_data.json
   ```

2. **Add new month entry**
   ```json
   "February_2026": {
     "month": "February 2026",
     "stats": {
       "schools": 940000,
       "teachers": 4360000,
       ...
     },
     ...
   }
   ```

3. **Rebuild vector database**
   ```bash
   docker-compose restart backend
   ```

### Data Structure

Each month contains:
- **stats**: Key numerical metrics
- **highlights**: Bullet points of achievements
- **events**: Notable events with dates
- **state_performance**: State-wise metrics
- **infrastructure**: Digital infrastructure data

---

## Deployment

### Production Deployment

1. **Update environment**
   ```bash
   cp .env.example .env.production
   # Edit with production settings
   ```

2. **Configure HTTPS** (recommended: Let's Encrypt)
   ```bash
   # Update nginx.conf with SSL configuration
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Set up monitoring**
   - Configure health check endpoints
   - Set up log aggregation
   - Monitor GPU/CPU usage for LLM

### Performance Optimization

- **LLM Model**: Use quantized models (Q4_K_M) for faster inference
- **Vector DB**: Pre-build FAISS index for production
- **Caching**: Enable Redis for frequently accessed data
- **CDN**: Serve static assets via CDN

---

## Security Considerations

### Implemented Security

- Rate limiting on API endpoints
- CORS configuration
- Input validation and sanitization
- No exposed API keys
- Secure headers (X-Frame-Options, CSP)

### Additional Recommendations

- Enable HTTPS in production
- Implement authentication (OAuth 2.0)
- Regular security audits
- Database encryption at rest
- API key rotation

---

## Troubleshooting

### Common Issues

**1. LLM not responding**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
docker restart education-dashboard-ollama
```

**2. Vector database not initialized**
```bash
# Rebuild vector database
rm -rf vector_db/
docker-compose restart backend
```

**3. Frontend not loading**
```bash
# Check backend connectivity
curl http://localhost:8000/api/health

# Check CORS settings in .env
```

**4. Out of memory errors**
```bash
# Use smaller LLM model
ollama pull mistral:7b-instruct-q4_K_M

# Or increase Docker memory limit
```

---

## Performance Targets

- **Page Load**: < 2 seconds
- **Chatbot Response**: < 3 seconds
- **Chart Animations**: 60fps
- **API Response Time**: < 500ms
- **Vector Search**: < 100ms

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

---

## Contributing

This is a government project. External contributions require:
1. Security clearance verification
2. Signed NDA
3. Code review by security team
4. Compliance certification

---

## License

Copyright © 2026 Ministry of Education, Government of India
All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## Contact

**Project Lead**: Ministry of Education, Government of India
**Technology Partner**: Deloitte Touche Tohmatsu
**Technical Support**: education-dashboard@deloitte.com

---

## Acknowledgments

- Ministry of Education for requirements and data
- Deloitte T&T for technical implementation
- Ollama team for LLM infrastructure
- FAISS team for vector search capabilities

---

**Built with institutional credibility. Powered by AI.**
