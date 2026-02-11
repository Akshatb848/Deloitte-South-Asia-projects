# API Documentation

## Education Intelligence Dashboard API
**Version 1.0.0**

Base URL: `http://localhost:8000/api`

---

## Authentication

Currently, the API uses rate limiting without authentication.
For production, OAuth 2.0 authentication is recommended.

---

## Rate Limits

- Chat endpoint: 30 requests/minute
- Compare endpoint: 20 requests/minute
- Search endpoint: 40 requests/minute
- Other endpoints: 100 requests/minute

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check API and system health status.

**Response**
```json
{
  "status": "healthy",
  "llm_connected": true,
  "rag_initialized": true,
  "timestamp": "2026-02-11T10:30:00.000Z"
}
```

---

### 2. Chat (AI Assistant)

**POST** `/chat`

Send a query to the Education Intelligence Assistant.

**Request Body**
```json
{
  "query": "What was the attendance rate in June 2025?",
  "current_month": "June_2025",
  "include_visualization": true
}
```

**Response**
```json
{
  "response": "In June 2025, the attendance rate was 95.1%, showing an improvement from the previous month...",
  "sources": [
    {
      "month": "June 2025",
      "type": "overview",
      "score": 0.95
    }
  ],
  "visualization": {
    "type": "chart",
    "chartId": "trendsChart"
  },
  "timestamp": "2026-02-11T10:30:00.000Z"
}
```

**Example cURL**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare Kerala and Gujarat attendance",
    "current_month": "June_2025"
  }'
```

---

### 3. Compare

**POST** `/compare`

Compare entities (states, months) across metrics.

**Request Body**
```json
{
  "entities": ["Kerala", "Gujarat"],
  "metric": "attendance",
  "months": ["June_2025"]
}
```

**Response**
```json
{
  "comparison_data": {
    "response": "State Performance Comparison for June 2025:\n\nKerala:\n- Attendance Rate: 97.2%\n- APAAR Coverage: 99.5%\n\nGujarat:\n- Attendance Rate: 96.1%\n- APAAR Coverage: 98.2%",
    "sources": [...]
  },
  "entities": ["Kerala", "Gujarat"],
  "metric": "attendance"
}
```

---

### 4. Get Available Months

**GET** `/newsletter/months`

Get list of all available months in the dataset.

**Response**
```json
{
  "months": [
    "April_2025",
    "May_2025",
    "June_2025",
    ...
  ]
}
```

---

### 5. Get Month Data

**GET** `/newsletter/{month}`

Get complete data for a specific month.

**Parameters**
- `month` (path): Month key (e.g., "June_2025")

**Response**
```json
{
  "month": "June 2025",
  "stats": {
    "schools": 920000,
    "teachers": 4258000,
    "students": 107800000,
    "apaar_ids": 125000000,
    "attendance_rate": 95.1,
    "teacher_tracking": 92.8
  },
  "highlights": [...],
  "events": [...],
  "state_performance": {...},
  "infrastructure": {...}
}
```

---

### 6. Semantic Search

**POST** `/search`

Perform semantic search across newsletter content.

**Query Parameters**
- `query` (required): Search query
- `top_k` (optional): Number of results (default: 5)

**Response**
```json
{
  "results": [
    {
      "text": "Month: June 2025...",
      "month": "June_2025",
      "type": "overview",
      "score": 0.92,
      "metadata": {...}
    }
  ]
}
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## Error Responses

```json
{
  "detail": "Error message description"
}
```

---

## Examples

### Python

```python
import requests

# Chat query
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "query": "Show me teacher tracking trends",
        "current_month": "June_2025"
    }
)

data = response.json()
print(data["response"])
```

### JavaScript

```javascript
// Chat query
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'What were the key highlights in June?',
    current_month: 'June_2025'
  })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

### cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Get month data
curl http://localhost:8000/api/newsletter/June_2025

# Search
curl -X POST "http://localhost:8000/api/search?query=teacher%20training&top_k=3"
```

---

## Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

**Last Updated**: February 11, 2026
