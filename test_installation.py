#!/usr/bin/env python3
"""
Installation Test Script
Verifies all dependencies are correctly installed (Python 3.10+)
"""

import sys
import importlib.metadata

def check_python_version():
    """Check Python version (3.10 or newer is supported)"""
    version = sys.version_info
    minimum = (3, 10)

    print("Checking Python version...")
    print(f"  Current: {version.major}.{version.minor}.{version.micro}")

    if (version.major, version.minor) >= minimum:
        print("  ✓ Python 3.10+ detected")
        return True
    print(f"  ⚠ Python 3.10+ required, got {version.major}.{version.minor}.{version.micro}")
    return False

def check_package(package_name, expected_version=None):
    """Check if a package is installed"""
    try:
        version = importlib.metadata.version(package_name)
        status = "✓"

        if expected_version and not version.startswith(expected_version.split('.')[0]):
            status = "⚠"

        print(f"  {status} {package_name}: {version}")
        return True
    except importlib.metadata.PackageNotFoundError:
        print(f"  ✗ {package_name}: NOT INSTALLED")
        return False

def test_imports():
    """Test critical imports"""
    print("\nTesting critical imports...")

    imports = [
        ("fastapi", "FastAPI framework"),
        ("pydantic", "Data validation"),
        ("numpy", "Numerical computing"),
        ("sentence_transformers", "Embeddings"),
        ("faiss", "Vector database"),
        ("httpx", "HTTP client"),
        ("uvicorn", "ASGI server"),
    ]

    success = True
    for module, description in imports:
        try:
            __import__(module)
            print(f"  ✓ {module} ({description})")
        except ImportError as e:
            print(f"  ✗ {module} ({description}): {e}")
            success = False

    return success

def test_sentence_transformers():
    """Test sentence transformers functionality"""
    print("\nTesting Sentence Transformers...")
    try:
        from sentence_transformers import SentenceTransformer  # noqa: F401

        print("  ✓ Sentence Transformers import successful")
        print("  Note: First run will download model (~400MB)")

        # Try to load model (will download on first run)
        # model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        # print("  ✓ Model loaded successfully")

        return True
    except Exception as e:
        print(f"  ✗ Sentence Transformers test failed: {e}")
        return False

def test_faiss():
    """Test FAISS functionality"""
    print("\nTesting FAISS...")
    try:
        import faiss
        import numpy as np

        # Create a simple index
        d = 64
        index = faiss.IndexFlatL2(d)
        print(f"  ✓ FAISS index created (dimension={d})")

        # Add some vectors
        nb = 100
        np.random.seed(1234)
        xb = np.random.random((nb, d)).astype('float32')
        index.add(xb)
        print(f"  ✓ Added {nb} vectors to index")

        # Search
        k = 4
        xq = np.random.random((1, d)).astype('float32')
        D, I = index.search(xq, k)
        print(f"  ✓ Search successful (k={k})")

        return True
    except Exception as e:
        print(f"  ✗ FAISS test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("Education Intelligence Dashboard - Installation Test")
    print("=" * 70)
    print()

    results = []

    # Check Python version
    results.append(("Python Version", check_python_version()))
    print()

    # Check packages
    print("Checking installed packages...")
    packages = [
        ("fastapi", None),
        ("pydantic", None),
        ("numpy", None),
        ("sentence-transformers", None),
        ("faiss-cpu", None),
        ("httpx", None),
        ("uvicorn", None),
        ("slowapi", None),
        ("python-dotenv", None),
    ]

    package_results = []
    for pkg, version in packages:
        package_results.append(check_package(pkg, version))

    results.append(("Package Installation", all(package_results)))
    print()

    # Test imports
    results.append(("Critical Imports", test_imports()))
    print()

    # Test FAISS
    results.append(("FAISS Functionality", test_faiss()))
    print()

    # Test Sentence Transformers
    results.append(("Sentence Transformers", test_sentence_transformers()))
    print()

    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("✓ All tests passed! Installation is successful.")
        print()
        print("Next steps:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Pull model: ollama pull mistral:7b-instruct")
        print("  3. Start backend: python backend/main.py")
        print("  4. Access dashboard: http://localhost:8080")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print()
        print("Troubleshooting:")
        print("  1. Ensure Python 3.10+ is installed")
        print("  2. Run: pip install -r requirements.txt")
        print("  3. Check docs/PYTHON_COMPATIBILITY.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
