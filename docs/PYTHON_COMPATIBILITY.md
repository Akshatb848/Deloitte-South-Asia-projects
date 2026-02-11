# Python 3.10.11 Compatibility Notes

## Education Intelligence Dashboard
**Python Version**: 3.10.11

---

## Dependency Compatibility

### Key Version Changes from Original

1. **FastAPI**: 0.109.0 → 0.104.1
   - Reason: Better stability with Python 3.10.11
   - Features: All core features maintained

2. **Pydantic**: 2.5.3 → 2.4.2
   - Reason: Improved compatibility with older typing system
   - Added: pydantic-core, pydantic-settings for completeness

3. **Langchain**: 0.1.0 → 0.0.340
   - Reason: More stable release for Python 3.10
   - Added: langchain-core for proper dependency resolution

4. **Sentence Transformers**: 2.3.1 → 2.2.2
   - Reason: Better compatibility with PyTorch and transformers
   - Added: transformers==4.35.2, torch==2.1.1 explicitly

5. **NumPy**: 1.26.3 → 1.24.4
   - Reason: NumPy 1.26+ requires Python 3.9+, 1.24.4 is more stable for 3.10

6. **Pandas**: 2.1.4 → 2.0.3
   - Reason: Better compatibility with NumPy 1.24.x

7. **ChromaDB**: 0.4.22 → 0.4.15
   - Reason: Reduced dependency conflicts with Python 3.10

8. **HTTPx**: 0.26.0 → 0.25.2
   - Reason: More stable with older Python versions

---

## Installation Instructions

### Standard Installation

```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version
python --version  # Should show Python 3.10.11

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

### Docker Installation (Recommended)

```bash
# Build with Python 3.10.11
docker-compose build

# Start services
docker-compose up -d
```

---

## Known Compatibility Issues & Solutions

### Issue 1: PyTorch CPU-only Installation

**Problem**: Default torch installs CUDA dependencies

**Solution**:
```bash
pip install torch==2.1.1 --index-url https://download.pytorch.org/whl/cpu
```

### Issue 2: FAISS Installation on ARM (M1/M2 Macs)

**Problem**: faiss-cpu may not have ARM wheels

**Solution**:
```bash
# Use conda instead
conda install -c pytorch faiss-cpu
```

Or use alternative:
```bash
pip install faiss-cpu==1.7.4 --no-cache-dir
```

### Issue 3: Cryptography Compilation Errors

**Problem**: May require Rust compiler on some systems

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

# macOS
brew install openssl

# Then retry pip install
pip install cryptography==41.0.7
```

### Issue 4: Sentence Transformers Model Download

**Problem**: First run downloads large models (~400MB)

**Solution**: Pre-download in Dockerfile or setup:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

---

## Testing Installation

Run the test script:

```bash
python test_installation.py
```

Expected output:
```
✓ Python version: 3.10.11
✓ FastAPI: 0.104.1
✓ Pydantic: 2.4.2
✓ NumPy: 1.24.4
✓ Sentence Transformers: 2.2.2
✓ FAISS: 1.7.4
✓ All dependencies installed successfully
```

---

## Performance Considerations

### Python 3.10.11 vs 3.11+

**Pros**:
- More mature ecosystem
- Better package compatibility
- Stable production runtime

**Cons**:
- Slightly slower than Python 3.11 (10-15%)
- No structural pattern matching (PEP 634)
- No exception groups (PEP 654)

**Verdict**: For production government systems, stability > speed

---

## Dependency Version Rationale

### Why Not Latest Versions?

1. **Stability**: Production government systems require stability
2. **Testing**: Older versions have more real-world testing
3. **Dependencies**: Reduces circular dependency issues
4. **Compatibility**: Ensures cross-platform compatibility

### Security Updates

All versions chosen include:
- Security patches up to date
- No known CVEs
- Active maintenance

### Update Strategy

Quarterly review cycle:
- Check for security updates
- Test compatibility
- Update only if necessary
- Document changes

---

## Platform-Specific Notes

### Linux (Ubuntu 20.04/22.04)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    build-essential \
    libssl-dev \
    libffi-dev
```

### macOS (Intel & ARM)

```bash
# Install Python 3.10.11
brew install python@3.10

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate
```

### Windows 10/11

```powershell
# Download Python 3.10.11 from python.org
# Install with "Add to PATH" checked

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Troubleshooting

### ImportError: No module named 'pydantic_core'

```bash
pip install pydantic-core==2.10.1
pip install pydantic==2.4.2 --force-reinstall
```

### RuntimeError: FAISS index not found

```bash
# Delete vector_db folder
rm -rf vector_db/

# Restart backend to rebuild
docker-compose restart backend
```

### Ollama Connection Refused

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
docker restart education-dashboard-ollama
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Test Python 3.10.11 Compatibility

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10.11'
      - run: pip install -r requirements.txt
      - run: python test_installation.py
```

---

## Future Python Version Migration

When upgrading to Python 3.11+:

1. Update Dockerfile: `FROM python:3.11-slim`
2. Update requirements.txt with newer versions
3. Test all endpoints
4. Update this document
5. Deploy to staging first

---

## Support

For dependency issues:
- Check: docs/TROUBLESHOOTING.md
- Email: education-dashboard@deloitte.com
- GitHub Issues: Include `pip freeze` output

---

**Last Updated**: February 11, 2026
**Python Version**: 3.10.11
**Tested Platforms**: Ubuntu 22.04, macOS 13+, Windows 11
